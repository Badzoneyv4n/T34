# run.py

import threading, asyncio

from bot.core.listener import start_bot
from bot.utils.reporter import run_auto_report_loop
from bot.core.manager import run_manager
from api_worker import run_api_worker
from bot.main import up  # This is your Updater instanc

threads = [
    threading.Thread(target=lambda: asyncio.run(start_bot()), name="Listener"), # type: ignore
    threading.Thread(target=run_api_worker, name="APIWorker"),
    threading.Thread(target=run_manager, name="Manager"),
    threading.Thread(target=up.start_polling, name="TelegramBot"),
    threading.Thread(target=run_auto_report_loop, name="AutoReport")
]

print("🚀 Launching T34 Boss-Bridge-Worker...")

for thread in threads:
    thread.start()
    print(f"✅ {thread.name} started.")

###########################################################################################
##############################TESTING PURPOSES ONLY (Simulate trades after starting the bot) ##################################

# import time
# from datetime import datetime, timedelta
# from dotenv import load_dotenv
# from bot.utils.session import SignalSession
# from bridge import commands_queue
# import pytz

# # Wait for threads to spin up
# time.sleep(15)

# # Load environment variables from .env file
# load_dotenv()

# user_timezone = os.getenv("TZ", '')  # fallback if missing
# if user_timezone == '':
#     raise ValueError("Please set your timezone in .env file as TZ=Your/Timezone")

# local_tz = pytz.timezone(user_timezone)
# now = datetime.now(local_tz)

# # Create a simulated session (entry in 20 seconds)
# session = SignalSession(
#     pair="EURUSD_otc",
#     expiration=60,
#     direction="call",
#     entry_time=now + timedelta(seconds=20),
#     martingale_levels=[
#         now + timedelta(seconds=120),
#         now + timedelta(seconds=180),
#     ],
#     initial_amount=1.0
# )

# # commands_queue.put({
# #     "action": "trade",
# #     "session": session
# # })

# print(f"🚀 Injected test session at {datetime.now().strftime('%H:%M:%S')}")

#######################################################################################

for thread in threads:
    thread.join()
    print(f"✅ {thread.name} finished.")
