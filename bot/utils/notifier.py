# bot/utils/notifier.py

import os
from dotenv import load_dotenv
from telegram import Bot

from bot.utils.session import SignalSession
from bot.utils.reporter import add_flags_to_pair, direction_emoji


load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("Tel_CHAT_ID")

bot = Bot(token=BOT_TOKEN) # type: ignore

def notify_signal(signal: dict):
    """
    Sends a well-formatted parsed signal to the Telegram channel.
    """
    flags = add_flags_to_pair(signal.get('pair', ''))
    direction = direction_emoji(signal.get('direction', ''))
    martingale = "⇨ " + "\n⇨ ".join(signal.get('martingale_levels', []))

    msg = (
        f"🚨 *🄽🄴🅆 🅂🄸🄶🄽🄰🄻*\n\n"
        f"✧ ͎𝐏͎𝐚͎𝐢͎𝐫͎: {flags}\n"
        f"✧ 𝐄͎𝐱͎𝐩͎𝐢͎𝐫͎𝐚͎𝐭͎𝐢͎𝐨͎𝐧͎: {signal.get('expiration')} min\n"
        f"✧ 𝐄͎𝐧͎𝐭͎𝐫͎𝐲͎ ͎𝐓͎𝐢͎𝐦͎𝐞͎: {signal.get('entry_time')}\n"
        f"✧ 𝐃͎𝐢͎𝐫͎𝐞͎𝐜͎𝐭͎𝐢͎𝐨͎𝐧͎: {direction}\n"
        f"✧ 𝐌͎𝐚͎𝐫͎𝐭͎𝐢͎𝐧͎𝐠͎𝐚͎𝐥͎𝐞͎ ͎𝐋͎𝐞͎𝐯͎𝐞͎𝐥͎𝐬͎:\n{martingale}"
    )

    bot.send_message(
        chat_id=CHAT_ID,
        text=msg,
        parse_mode='Markdown'
    )

def notify_trade_placed(pair, entry_time, amount, order_id, direction , level=0):
    """
    Notifies when a trade is placed.
    """
    flags = add_flags_to_pair(pair)
    direction_icon = direction_emoji(direction)

    entry_time_str = entry_time.strftime("%H:%M") if hasattr(entry_time, "strftime") else str(entry_time)
    level_str = f"🎯 𝐌𝐚𝐫𝐭𝐢𝐧𝐠𝐚𝐥𝐞 𝐋𝐞𝐯𝐞𝐥: {level}" if level > 0 else "🚀 𝐄𝐧𝐭𝐫𝐲 𝐋𝐞𝐯𝐞𝐥: 𝐃𝐢𝐫𝐞𝐜𝐭 (𝐈𝐧𝐢𝐭𝐢𝐚𝐥)"
    
    msg = (
        f"📈 *🆃🆁🅰🅳🅴 🅿🅻🅰🅲🅴🅳*\n\n"
        f"✧ {level_str}\n\n"
        f"✧ 𝐏𝐚𝐢𝐫: {flags}\n"
        f"✧ 𝐄𝐧𝐭𝐫𝐲: {entry_time_str}\n"
        f"✧ 𝐃𝐢𝐫𝐞𝐜𝐭𝐢𝐨𝐧: {direction_icon}\n"
        f"✧ 𝐀𝐦𝐨𝐮𝐧𝐭: ${amount:.2f}\n"
        f"✧ 𝐎𝐫𝐝𝐞𝐫 𝐈𝐃: `{order_id}`"
    )

    bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode='Markdown')

def notify_trade_result(session, balance):
    
    details = []
    
    def result_emoji_label(result: str) -> str:
        result = result.lower()
        if result == "win":
            return "✅ *WIN*"
        elif result == "loss":
            return "❌ *LOSS*"
        elif result == "draw":
            return "⚪ *DRAW*"
        return "❓ *UNKNOWN*"


    for t in session.trades:
        flags = add_flags_to_pair(session.pair)
        dir_icon = direction_emoji(session.direction)
        time_str = t.entry_time.strftime("%H:%M")
        result_label = result_emoji_label(t.result)
        details.append(
            f"{flags} {dir_icon} | {time_str} | Level {t.level+1} | {result_label} | Profit: ${t.profit:.2f}"
        )

    msg = (
        f"✅ *【﻿Ｓｉｇｎａｌ　Ｒｅｓｕｌｔ】*\n\n"
        f"{chr(10).join(details)}\n\n"
        f"𝙏𝙤𝙩𝙖𝙡 𝙋/𝙇: ${session.total_profit:.2f}\n"
        f"𝙐𝙥𝙙𝙖𝙩𝙚𝙙 𝘽𝙖𝙡𝙖𝙣𝙘𝙚: ${balance:.2f}"
    )
    bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode="Markdown")

def notify_bot_connected():
    msg = "🤖 𝐵𝑜𝓉 𝒾𝓈 𝓃𝑜𝓌 𝒸𝑜𝓃𝓃𝑒𝒸𝓉𝑒𝒹 𝒶𝓃𝒹 𝓇𝑒𝒶𝒹𝓎 𝓉𝑜 𝓉𝓇𝒶𝒹𝑒!"
    bot.send_message(chat_id=CHAT_ID, text=msg)

def notify_bot_connection_failed():
    msg = "❌ 𝐵𝑜𝓉 𝒸𝑜𝓃𝓃𝑒𝒸𝓉𝒾𝑜𝓃 𝒻𝒶𝒾𝓁𝑒𝒹. 𝒫𝓁𝑒𝒶𝓈𝑒 𝒸𝒽𝑒𝒸𝓀 𝓎𝑜𝓊𝓇 𝒸𝑜𝓃𝒻𝒾𝑔𝓊𝓇𝒶𝓉𝒾𝑜𝓃."
    bot.send_message(chat_id=CHAT_ID, text=msg)

def notify_balance(bal):
    msg = f"💰 *𝐁𝐚𝐥𝐚𝐧𝐜𝐞 𝐔𝐩𝐝𝐚𝐭𝐞*: ${bal:.2f}"
    bot.send_message(chat_id=CHAT_ID, text=msg)

def notify_report(report: str):
    """
    Sends the generated report to the target chat.
    """
    if not report:
        report = "📋 𝗡𝗼 𝘁𝗿𝗮𝗱𝗲𝘀 𝘆𝗲𝘁 𝘁𝗼𝗱𝗮𝘆!"
    
    bot.send_message(
        chat_id=CHAT_ID,
        text=report,
        parse_mode='Markdown'
    )