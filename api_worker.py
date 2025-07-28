# api_worker.py

import time, os, asyncio
from dotenv import load_dotenv

from bridge import *
from pocketoptionapi.stable_api import PocketOption
from bot.utils.scheduler import execute_signal
from bot.utils.balance_manager import BalanceManager


# Load environment variables from .env file
load_dotenv()

HEARTBEAT_INTERVAL = 600  # 10 min

# PocketOption config
DEMO = os.getenv("DEMO", "True").lower() == "true"  # or False for real

if DEMO:
    SSID = os.getenv('PO_SSID').replace("\\", '') # type: ignore
else:
    SSID = os.getenv('PO_SSID')

user_timezone = os.getenv("TZ", '')  # fallback if missing
if user_timezone == '':
    raise ValueError("Please set your timezone in .env file as TZ=Your/Timezone")

def run_api_worker():
    """
    Starts the API worker to handle commands and results.
    """
    # 🟢 Create an event loop for this thread
    asyncio.set_event_loop(asyncio.new_event_loop())

    api = PocketOption(SSID, DEMO)
    connected = api.connect()

    time.sleep(3)  # Wait a bit for connection to stabilize

    print(f"[API] Connected: {connected} , Timezone: {user_timezone}")

    print(f"[API] Using SSID: {SSID}")  # Debugging line to check SSID

    bm = BalanceManager(balance=api.get_balance(), risk_per_signal=0.10, martingale_levels=3) # type: ignore

    print(bm.summary())  # ✅ Debug log

    # Heartbeat  checker
    last_check = time.time()
    heartbeat_interval = 600

    while True:
        # ✅ HEARTBEAT CHECK (every 10 minutes)
        if time.time() - last_check > heartbeat_interval:
            try:
                if api_lock.acquire(timeout=5):  # wait max 5s to avoid hanging
                    try:
                        balance = api.get_balance()
                        print(f"[HEARTBEAT] Checked balance: {balance}")
                    finally:
                        api_lock.release()
                else:
                    print("[HEARTBEAT] Skipped: API is locked (probably trading)")

            except Exception as e:
                print(f"[HEARTBEAT] Balance check failed: {e}")
                print("[HEARTBEAT] Reconnecting...")
                api.disconnect()
                time.sleep(3)
                api.connect()
            last_check = time.time()
        
        command = commands_queue.get()
        
        print("[API] Command pulled:", command)  # 👈 Add this!
        
        if command["action"] == "trade":
            
            # Stop if bot is deactivated
            if command["action"] == "trade":
                if not is_bot_active():
                    print("[API] ⚠️ Trade ignored: Bot is deactivated.")
                    results_queue.put({
                        "action": "trade_result",
                        "error": "bot_deactivated"
                    })
                    continue

            session = command["session"]

            # Now attach this to your SignalSession
            session.initial_amount = bm.calc_base_amount()

            profit, balance = execute_signal(session, api, bm.balance)

            bm.update_balance(balance) # type: ignore

            results_queue.put({"action": "trade_result", "session": session,  "balance": balance})
            print("[API] Result put:", {"action": "trade_result", "session": session})
        
        elif command["action"] == "get_balance":
            try:
                if api_lock.acquire(timeout=5):
                    try:
                        balance = api.get_balance()
                        print("[API] Raw balance from API.get_balance():", balance)
                    finally:
                        api_lock.release()
                else:
                    print("[API] Skipped get_balance: API busy")
                    balance = -1  # or return an error code/message
            except Exception as e:
                print(f"[API] Error getting balance: {e}")
                balance = -1

            reply_queue.put({
                "action": "balance",
                "balance": balance,
                "request_id": command.get("request_id")  # pass it through!
            })

        elif command["action"] == "restart_api":
            print("[API] 🔁 Restart requested by bot.")
            try:
                if api_lock.acquire(timeout=5):
                    try:
                        api.disconnect()
                        time.sleep(3)
                        api.connect()
                        balance = api.get_balance()
                        bm.update_balance(balance) # type: ignore

                        reply_queue.put({
                            "action": "api_restart",
                            "success": True,
                            "balance": balance,
                            "request_id": command.get("request_id")
                        })
                        print("[API] 🔁 Restart successful.")
                    finally:
                        api_lock.release()
                else:
                    print("[API] 🔁 Restart skipped: API is trading.")
                    reply_queue.put({
                        "action": "api_restart",
                        "success": False,
                        "balance": -1,
                        "request_id": command.get("request_id")
                    })
            except Exception as e:
                print(f"[API] 🔁 Restart failed: {e}")
                reply_queue.put({
                    "action": "api_restart",
                    "success": False,
                    "balance": -1,
                    "request_id": command.get("request_id")
                })