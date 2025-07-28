# bot/core/listener.py

import os
from telethon import events, TelegramClient
from dotenv import load_dotenv

from bot.utils.parser import parse_signal
from bot.utils.session import SignalSession
from bot.utils.utils import map_pair, convert_to_local
from .manager import send_trade
from bot.utils.notifier import notify_signal


# Load environment variables from .env file
load_dotenv()

# Get your API credentials
TEL_API_ID_str = os.getenv('Tel_API_ID')
TEL_API_HASH = os.getenv('Tel_API_HASH')
SESSION_NAME = 't34_session'

if TEL_API_ID_str is None:
    raise ValueError("Missing Tel_API_ID in .env")
TEL_API_ID: int = int(TEL_API_ID_str)

if TEL_API_HASH is None:
    raise ValueError("Missing TEL_API_HASH in .env")

Channel_name = 'yousefftraderofficial'

client: TelegramClient = TelegramClient(SESSION_NAME, TEL_API_ID, TEL_API_HASH)

@client.on(events.NewMessage(chats=Channel_name))
async def new_message_listener(event):
    """
    This function listens for new messages in the specified channel.
    """
    
    message = event.message.text or "[No text]"
    print(f"[New Signal] ➜ {message}")

    if not ("Expiration" in message and "Entry" in message and ("BUY" in message or "SELL" in message)):
        print("⚠️ Not a valid signal. Skipping.")
        return

    parsed = parse_signal(message)
    
    if parsed["pair"] is None or parsed["direction"] is None:
        print("❌ Not a valid parsed signal, skipping...")
        return

    notify_signal(parsed)

    pair = map_pair(parsed['pair'])
    expiration = 300  # 5M default
    direction = "call" if parsed['direction'].lower() == "buy" else "put"
    entry_time = convert_to_local(parsed['entry_time'])
    martingale_levels = [
        convert_to_local(level) for level in parsed['martingale_levels']
    ]

    session = SignalSession(
        pair=pair,
        expiration=expiration,
        direction=direction,
        entry_time=entry_time,
        martingale_levels=martingale_levels,
        initial_amount=1.0  # START with $1
    )

    send_trade(session)
    
async def start_bot():
    """
    Main function to start the Telegram client and listen for new messages.
    """
    print("✅ T34 Listener is up. Waiting for new messages...")
    await client.start() # type: ignore
    await client.run_until_disconnected() # type: ignore
    
    