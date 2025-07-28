# bot/main.py

import os
from dotenv import load_dotenv
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler

from bot.core.commands import *

# Load env vars
load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')

# Init Updater and Dispatcher
up = Updater(token=BOT_TOKEN, use_context=True) # type: ignore
dp = up.dispatcher

# Add command handlers
dp.add_handler(CommandHandler("start", start)) # type: ignore
dp.add_handler(CommandHandler("status", status)) # type: ignore
dp.add_handler(CommandHandler("menu", menu)) # type: ignore
dp.add_handler(CommandHandler("report", report)) # type: ignore
dp.add_handler(CommandHandler("activate", activate)) # type: ignore
dp.add_handler(CommandHandler("deactivate", deactivate)) # type: ignore

# 🟢 Handles buttons for your main menu buttons
dp.add_handler(CallbackQueryHandler(button, pattern="^(balance|status|stop|restart_api)$"))  # type: ignore

# 🟢 Handles buttons for report sessions
dp.add_handler(CallbackQueryHandler(report_button, pattern="^report_"))  # type: ignore

# Run bot
if __name__ == "__main__":
    print("🤖 T34 Bot is now running...")
    up.start_polling()
    up.idle()
