# bot/utils/reporter.py

from collections import defaultdict
from datetime import datetime, timedelta
import pytz, os, time
from dotenv import load_dotenv
from telegram import Bot

from bot.utils.session import SignalSession, TradeResult, ALL_SESSIONS

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("Tel_CHAT_ID")

bot = Bot(token=BOT_TOKEN) # type: ignore

# ---------------------------------------------------
# Reusable Mappings & Helpers
# ---------------------------------------------------

PAIR_FLAGS = {
    "GBP": "🇬🇧",
    "USD": "🇺🇸",
    "EUR": "🇪🇺",
    "JPY": "🇯🇵",
    "AUD": "🇦🇺",
    "NZD": "🇳🇿",
    "CHF": "🇨🇭",
    "CAD": "🇨🇦",
}

SESSION_EMOJIS = {
    "Morning": "🌤",
    "Afternoon": "☀️",
    "Night": "🌙",
    "OverNight": "🌑",
}

def get_session_name(entry_time):
    utc_minus4 = entry_time.astimezone(pytz.timezone('Etc/GMT+4'))
    hour = utc_minus4.hour
    if 6 <= hour < 12:
        return "Morning"
    elif 12 <= hour < 18:
        return "Afternoon"
    elif 18 <= hour < 24:
        return "Night"
    else:
        return "OverNight"

def add_flags_to_pair(pair):
    pair = pair.replace("_otc", "").replace("OTC", "").replace(" ", "").replace("//", "/").upper()
    
    # Ensure single "/"
    if "/" in pair:
        base, quote = pair.split("/", 1)
    else:
        base, quote = pair[:3], pair[3:]

    base, quote = base.strip(), quote.strip()
    return f"{PAIR_FLAGS.get(base, '')} {base}/{quote} {PAIR_FLAGS.get(quote, '')} OTC"

def direction_emoji(direction):
    return "🟢 Buy" if direction.lower() == "call" else "🔴 Sell"

def superscript(n):
    superscripts = {
        "0": "⁰", "1": "¹", "2": "²", "3": "³", "4": "⁴",
        "5": "⁵", "6": "⁶", "7": "⁷", "8": "⁸", "9": "⁹"
    }
    s = str(n)
    return ''.join(superscripts.get(ch, f"^{ch}") for ch in s)

def color_profit(pnl):
    return f"+{pnl:.2f}" if pnl >= 0 else f"-{abs(pnl):.2f}"

# ---------------------------------------------------
# Report Generator
# ---------------------------------------------------

def generate_report(specific_session=None):
    grouped = defaultdict(list)

    #FIXME: Prevent duplicate of trades in report

    seen_ids = set()

    for session in ALL_SESSIONS:
        uid = f"{session.pair}_{session.direction}_{session.entry_time.isoformat()}"
        if uid in seen_ids:
            continue
        seen_ids.add(uid)
        session_name = get_session_name(session.entry_time)
        grouped[session_name].append(session)

    sections = []

    for name in ["Morning", "Afternoon", "Night", "OverNight"]:
        if specific_session and name != specific_session:
            continue

        trades = grouped.get(name, [])
        if not trades:
            continue

        emoji = SESSION_EMOJIS.get(name, "")
        date_str = trades[0].entry_time.strftime("%A, %B %d, %Y")

        section = [
            f"📄 𝙍𝙀𝙋𝙊𝙍𝙏 ",
            f"{emoji} *{name.upper()} 𝐒𝐄𝐒𝐒𝐈𝐎𝐍*",
            f"🗓 {date_str}",
            f"#T34REPORT",
            ""
        ]

        section.append("```")
        wins, losses, total_pl = 0, 0, 0

        for idx, s in enumerate(trades, 1):
            trade_icon = "✅" if s.total_profit >= 0 else "❌"
            pair_flags = add_flags_to_pair(s.pair)
            time_str = s.entry_time.strftime("%H:%M")
            direction = direction_emoji(s.direction)
            mg_power = superscript(len(s.trades)-1)
            profit_str = color_profit(s.total_profit)

            if s.total_profit >= 0:
                wins += 1
            else:
                losses += 1

            line = f"{trade_icon}{superscript(idx)} • {pair_flags} • [{time_str}] • {direction} • MG{mg_power} • {profit_str}"
            section.append(line)
            total_pl += s.total_profit

        section.append("```")

        total_trades = wins + losses
        accuracy = (wins / total_trades) * 100 if total_trades > 0 else 0.0

        section.extend([
            f"✅ 𝘼𝙘𝙘𝙪𝙧𝙖𝙘𝙮: {accuracy:.2f}%",
            f"🟢 𝙒𝙞𝙣𝙨:{wins} ❌ 𝙇𝙤𝙨𝙨𝙚𝙨: {losses}",
            f"💵 𝙏𝙤𝙩𝙖𝙡 𝙋/𝙇: {color_profit(total_pl)}",
            ""
        ])

        sections.append("\n".join(section))

    final_report = "\n\n".join(sections) if sections else "📋 𝙉𝙤 𝙩𝙧𝙖𝙙𝙚𝙨 𝙮𝙚𝙩 𝙩𝙤𝙙𝙖𝙮!"
    return final_report

# ---------------------------------------------------
# For Testing: Populate fake sessions
# ---------------------------------------------------

SESSION_CLOSE_TIMES = {
    "Morning": {"hour": 12, "minute": 0},
    "Afternoon": {"hour": 18, "minute": 0},
    "Night": {"hour": 0, "minute": 0},
    "OverNight": {"hour": 6, "minute": 0}
}

def get_current_session_close_name():
    """Returns session name if its close time matches now, else None"""
    tz = pytz.timezone('Etc/GMT+4')
    now = datetime.now(tz)
    for name, t in SESSION_CLOSE_TIMES.items():
        if now.hour == t["hour"] and now.minute == t["minute"]:
            return name
    return None

def run_auto_report_loop():
    """Run this in a separate thread or add to your manager loop"""
    sent_today = set()
    print("✅ Auto-report scheduler running...")

    while True:
        session_name = get_current_session_close_name()
        today = datetime.now().strftime("%Y-%m-%d")

        if session_name:
            unique_key = f"{session_name}_{today}"
            if unique_key not in sent_today:
                report_text = generate_report(specific_session=session_name)
                bot.send_message(chat_id=CHAT_ID, text=report_text, parse_mode="Markdown")
                print(f"📋 Sent {session_name} auto-report")
                sent_today.add(unique_key)

        time.sleep(60)  # check every minute