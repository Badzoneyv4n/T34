# bot/utils/commands.py

import os, uuid, queue , time
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from threading import enumerate as list_threads

from bot.utils.reporter import generate_report
from bridge import activate_bot, deactivate_bot, is_bot_active

# Import the bridge queues!
from bridge import commands_queue, reply_queue

load_dotenv()
OWNER_ID = int(os.getenv("Tel_CHAT_ID")) # type: ignore # Replace with your actual owner ID

# ✅ Restriction decorator
def restricted(func):
    def wrapper(update: Update, context: CallbackContext, *args, **kwargs):
        user_id = update.effective_user.id # type: ignore
        if user_id != OWNER_ID:
            update.message.reply_text("🚫 𝐘𝐨𝐮 𝐚𝐫𝐞 𝐧𝐨𝐭 𝐚𝐮𝐭𝐡𝐨𝐫𝐢𝐳𝐞𝐝 𝐭𝐨 𝐮𝐬𝐞 𝐭𝐡𝐢𝐬 𝐛𝐨𝐭.")
            return
        return func(update, context, *args, **kwargs)
    return wrapper

@restricted
def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "🤖 𝗛𝗲𝗹𝗹𝗼 𝗯𝗼𝘀𝘀! 𝗧𝟯𝟰 𝗶𝘀 𝘂𝗽.\n 𝗨𝘀𝗲 /menu 𝘁𝗼 𝗼𝗽𝗲𝗻 𝘁𝗵𝗲 𝗰𝗼𝗺𝗺𝗮𝗻𝗱 𝗽𝗮𝗻𝗲𝗹."
    )

@restricted
def status(update: Update, context: CallbackContext):
    request_id = str(uuid.uuid4())

    # 📤 Send a balance check to API
    commands_queue.put({
        "action": "get_balance",
        "request_id": request_id
    })

    # ⏳ Setup timeout for reply
    start_time = time.time()
    timeout = 10

    api_status = "❌ 𝐀𝐏𝐈: 𝐍𝐨 𝐫𝐞𝐩𝐥𝐲"
    balance_text = ""

    while time.time() - start_time < timeout:
        try:
            result = reply_queue.get(timeout=timeout)
            if result.get("request_id") == request_id and result.get("action") == "balance":
                balance = result.get("balance")
                if balance == -1:
                    api_status = "⚠️ 𝐀𝐏𝐈: 𝐁𝐮𝐬𝐲 𝐨𝐫 𝐥𝐨𝐜𝐤𝐞𝐝"
                else:
                    api_status = "✅ 𝐀𝐏𝐈: 𝐑𝐞𝐬𝐩𝐨𝐧𝐝𝐢𝐧𝐠"
                    balance_text = f"💰 𝘽𝙖𝙡𝙖𝙣𝙘𝙚:${balance:.2f}"
                break
            else:
                reply_queue.put(result)  # not ours
        except queue.Empty:
            break

    # 🧵 Check threads
    active_threads = [t.name for t in list_threads()]

    telegram_ok = any("Bot:" in name for name in active_threads)
    telegram_status = "✅ 𝐓𝐞𝐥𝐞𝐠𝐫𝐚𝐦 𝐁𝐨𝐭: 𝐑𝐮𝐧𝐧𝐢𝐧𝐠" if telegram_ok else "❌ 𝐓𝐞𝐥𝐞𝐠𝐫𝐚𝐦 𝐁𝐨𝐭: 𝐍𝐨𝐭 𝐟𝐨𝐮𝐧𝐝"

    listener_ok = any("Listener" in name for name in active_threads)
    signal_status = "✅ 𝐋𝐢𝐬𝐭𝐞𝐧𝐞𝐫: 𝐑𝐮𝐧𝐧𝐢𝐧𝐠" if listener_ok else "❌ 𝐋𝐢𝐬𝐭𝐞𝐧𝐞𝐫: 𝐍𝐨𝐭 𝐟𝐨𝐮𝐧𝐝"

    api_worker_ok = any("APIWorker" in name for name in active_threads)
    api_thread_status = "✅ 𝐀𝐏𝐈 𝐖𝐨𝐫𝐤𝐞𝐫: 𝐑𝐮𝐧𝐧𝐢𝐧𝐠" if api_worker_ok else "❌ 𝐀𝐏𝐈 𝐖𝐨𝐫𝐤𝐞𝐫: 𝐍𝐨𝐭 𝐫𝐮𝐧𝐧𝐢𝐧𝐠"

    manager_ok = any("Manager" in name for name in active_threads)
    manager_status = "✅ 𝐌𝐚𝐧𝐚𝐠𝐞𝐫: 𝐑𝐮𝐧𝐧𝐢𝐧𝐠" if manager_ok else "❌ 𝐌𝐚𝐧𝐚𝐠𝐞𝐫: 𝐍𝐨𝐭 𝐟𝐨𝐮𝐧𝐝"

    auto_report_ok = any("AutoReport" in name for name in active_threads)
    auto_report_status = "✅ 𝐀𝐮𝐭𝐨𝐑𝐞𝐩𝐨𝐫𝐭: 𝐑𝐮𝐧𝐧𝐢𝐧𝐠" if auto_report_ok else "❌ 𝐀𝐮𝐭𝐨𝐑𝐞𝐩𝐨𝐫𝐭: 𝐍𝐨𝐭 𝐫𝐮𝐧𝐧𝐢𝐧𝐠"

    # 📦 Compose final reply
    update.message.reply_text(
        f"🤖 *𝙏34 𝙎𝙮𝙨𝙩𝙚𝙢 𝙎𝙩𝙖𝙩𝙪𝙨*\n\n"
        f"{telegram_status}\n"
        f"{signal_status}\n"
        f"{manager_status}\n"
        f"{api_thread_status}\n"
        f"{auto_report_status}\n"
        f"{api_status}\n\n"
        f"{balance_text}",
        parse_mode='Markdown'
    )


@restricted
def activate(update: Update, context: CallbackContext):
    activate_bot()
    update.message.reply_text("✅ 𝘽𝙤𝙩 𝙞𝙨 𝙣𝙤𝙬 *𝙖𝙘𝙩𝙞𝙫𝙖𝙩𝙚𝙙* 𝙖𝙣𝙙 𝙬𝙞𝙡𝙡 𝙥𝙧𝙤𝙘𝙚𝙨𝙨 𝙩𝙧𝙖𝙙𝙚𝙨.\n\n𝙏𝙤 *𝙙𝙞𝙨𝙘𝙤𝙣𝙣𝙚𝙘𝙩*, 𝙧𝙪𝙣 /deactivate", parse_mode='Markdown')

@restricted
def deactivate(update: Update, context: CallbackContext):
    deactivate_bot()
    update.message.reply_text("⛔ 𝘽𝙤𝙩 𝙞𝙨 𝙣𝙤𝙬 *𝙙𝙚𝙖𝙘𝙩𝙞𝙫𝙖𝙩𝙚𝙙* 𝙖𝙣𝙙 𝙬𝙞𝙡𝙡 𝙞𝙜𝙣𝙤𝙧𝙚 𝙩𝙧𝙖𝙙𝙚𝙨.\n\n𝙏𝙤 *𝙧𝙚𝙘𝙤𝙣𝙣𝙚𝙘𝙩*, 𝙧𝙪𝙣 /activate", parse_mode='Markdown')

@restricted
def menu(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("💰 𝗕𝗮𝗹𝗮𝗻𝗰𝗲", callback_data='balance')],
        [InlineKeyboardButton("🔌 𝗕𝗼𝘁 𝗦𝘁𝗮𝘁𝘂𝘀", callback_data='status')],
        [InlineKeyboardButton("🛑 𝗦𝘁𝗼𝗽 𝗕𝗼𝘁", callback_data='stop')],
        [InlineKeyboardButton("🔁 𝗥𝗲𝘀𝘁𝗮𝗿𝘁 𝗣𝗢 𝗔𝗣𝗜", callback_data='restart_api')]

    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        '📋 *𝙏̲3̲4̲ ̲𝘽̲𝙤̲𝙨̲𝙨̲ ̲𝘾̲𝙤̲𝙣̲𝙩̲𝙧̲𝙤̲𝙡̲ ̲𝙈̲𝙚̲𝙣̲𝙪̲*',
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

@restricted
def button(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    query.answer()

    if user_id != OWNER_ID:
        query.edit_message_text("🚫 𝙔𝙤𝙪 𝙖𝙧𝙚 𝙣𝙤𝙩 𝙖𝙪𝙩𝙝𝙤𝙧𝙞𝙯𝙚𝙙 𝙩𝙤 𝙪𝙨𝙚 𝙩𝙝𝙞𝙨 𝙗𝙤𝙩.")
        return

    data = query.data

    if data == "balance":
        # 🚀 Send balance request to API
        request_id = str(uuid.uuid4())

        commands_queue.put({
            "action": "get_balance",
            "request_id": request_id
        })

        timeout = 10
        start_time = time.time()

        while True:
            elapsed = time.time() - start_time
            if elapsed > timeout:
                query.edit_message_text("⚠️ 𝙉𝙤 𝙧𝙚𝙥𝙡𝙮 𝙛𝙧𝙤𝙢 𝘼𝙋𝙄. 𝙏𝙧𝙮 𝙖𝙜𝙖𝙞𝙣.")
                return

            try:
                result = reply_queue.get(timeout=timeout - elapsed)

                if result.get("request_id") == request_id:
                    balance = result.get("balance")
                    if balance == -1:
                        query.edit_message_text("⚠️ 𝘼𝙋𝙄 𝙞𝙨 𝙘𝙪𝙧𝙧𝙚𝙣𝙩𝙡𝙮 𝙗𝙪𝙨𝙮. 𝙏𝙧𝙮 𝙖𝙜𝙖𝙞𝙣.")
                    else:
                        query.edit_message_text(text=f"💰 𝘽𝙖𝙡𝙖𝙣𝙘𝙚: ${balance:.2f}")
                    break
                else:
                    # unrelated result — put it back
                    reply_queue.put(result)

            except queue.Empty:
                query.edit_message_text("⚠️ 𝙉𝙤 𝙧𝙚𝙥𝙡𝙮 𝙛𝙧𝙤𝙢 𝘼𝙋𝙄. 𝙏𝙧𝙮 𝙖𝙜𝙖𝙞𝙣.")
                return


        
        
    elif data == "status":
        # Remove the inline keyboard from the control menu
        query.edit_message_reply_markup(reply_markup=None)

        # Forward to the real /status command logic
        # We must fake `.message` because `status()` expects update.message not update.callback_query
        update.message = query.message  # ✅ this tricks it into working
        status(update, context)


    elif data == "stop":
        query.edit_message_reply_markup(reply_markup=None)  # hide menu
        update.message = query.message
        deactivate(update, context)
    
    elif data == "restart_api":
        query.answer()
        request_id = str(uuid.uuid4())

        commands_queue.put({
            "action": "restart_api",
            "request_id": request_id
        })

        try:
            result = reply_queue.get(timeout=15)
            if result.get("request_id") == request_id:
                success = result.get("success")
                balance = result.get("balance")

                if success:
                    query.edit_message_text(f"🔁 𝐀𝐏𝐈 𝐫𝐞𝐬𝐭𝐚𝐫𝐭𝐞𝐝!\n💰 𝐁𝐚𝐥𝐚𝐧𝐜𝐞: ${balance:.2f}")
                else:
                    query.edit_message_text("❌ 𝐅𝐚𝐢𝐥𝐞𝐝 𝐭𝐨 𝐫𝐞𝐬𝐭𝐚𝐫𝐭 𝐀𝐏𝐈. 𝐂𝐡𝐞𝐜𝐤 𝐥𝐨𝐠𝐬.")
            else:
                reply_queue.put(result)
                query.edit_message_text("⚠️ 𝐀𝐏𝐈 𝐬𝐞𝐧𝐭 𝐮𝐧𝐫𝐞𝐥𝐚𝐭𝐞𝐝 𝐫𝐞𝐬𝐩𝐨𝐧𝐬𝐞.")
        except queue.Empty:
            query.edit_message_text("❌ 𝐓𝐢𝐦𝐞𝐨𝐮𝐭. 𝐀𝐏𝐈 𝐝𝐢𝐝 𝐧𝐨𝐭 𝐫𝐞𝐬𝐩𝐨𝐧𝐝.")

    else:
        query.edit_message_text("❓ 𝙐𝙣𝙠𝙣𝙤𝙬𝙣 𝙘𝙤𝙢𝙢𝙖𝙣𝙙.")

@restricted
def report(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("🌤 𝐌𝐨𝐫𝐧𝐢𝐧𝐠", callback_data='report_morning')],
        [InlineKeyboardButton("☀️ 𝐀𝐟𝐭𝐞𝐫𝐧𝐨𝐨𝐧", callback_data='report_afternoon')],
        [InlineKeyboardButton("🌙 𝐍𝐢𝐠𝐡𝐭", callback_data='report_night')],
        [InlineKeyboardButton("🌑 𝐎𝐯𝐞𝐫𝐍𝐢𝐠𝐡𝐭", callback_data='report_overnight')]
    ]
    markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        "📋 *𝙎𝙚𝙡𝙚𝙘𝙩 𝙨𝙚𝙨𝙨𝙞𝙤𝙣 𝙩𝙤 𝙜𝙚𝙣𝙚𝙧𝙖𝙩𝙚 𝙧𝙚𝙥𝙤𝙧𝙩:*",
        parse_mode='Markdown',
        reply_markup=markup
    )


# Add callback handler too:
def report_button(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    data = query.data
    session_map = {
        'report_morning': "Morning",
        'report_afternoon': "Afternoon",
        'report_night': "Night",
        'report_overnight': "OverNight",
    }

    session_name = session_map.get(data)
    if not session_name:
        query.edit_message_text("❓ 𝐔𝐧𝐤𝐧𝐨𝐰𝐧 𝐬𝐞𝐬𝐬𝐢𝐨𝐧.")
        return

    report_text = generate_report(specific_session=session_name)
    if not report_text:
        query.edit_message_text(f"📋 {session_name} 𝐬𝐞𝐬𝐬𝐢𝐨𝐧 𝐧𝐨𝐭 𝐬𝐭𝐚𝐫𝐭𝐞𝐝 𝐨𝐫 𝐢𝐧 𝐩𝐫𝐨𝐠𝐫𝐞𝐬𝐬.")
    else:
        query.edit_message_text(report_text, parse_mode='Markdown')



