# bot/core/manager.py

import pytz
from datetime import datetime

from bridge import commands_queue, results_queue
from bot.utils.notifier import *
from bot.utils.reporter import get_session_name, generate_report
from bot.utils.session import ALL_SESSIONS


def send_trade(session):
    """
    Sends the trade session to the API for execution.
    """
    cmd = {
        "action": "trade",
        "session": session  # make sure SignalSession has .to_dict()
    }
    print("[BRIDGE] Command put:", cmd)
    commands_queue.put(cmd)


def request_balance():
    """
    Requests the current balance from the API.
    """
    cmd = {"action": "get_balance"}
    print("[BRIDGE] Command put:", cmd)
    commands_queue.put(cmd)

def check_and_notify_report(last_session):
    """
    Checks if session ended. If yes, auto-send report.
    """
    last_session_name = get_session_name(last_session.entry_time)
    local_now = datetime.now(pytz.timezone('Etc/GMT+4'))
    now_session_name = get_session_name(local_now)

    if last_session_name != now_session_name:
        print(f"[MANAGER] {last_session_name} ended. Sending auto-report...")
        report = generate_report(specific_session=last_session_name)
        notify_report(report)

def reset_sessions_if_new_day():
    """
    Clears ALL_SESSIONS if new day (Morning session).
    """
    utc_minus4 = datetime.now(pytz.timezone('Etc/GMT+4'))
    if utc_minus4.hour == 6 and utc_minus4.minute < 5:
        ALL_SESSIONS.clear()
        print("[MANAGER] All sessions reset for new day.")

def run_manager():
    """
    Starts the manager to handle commands and results.
    """
    while True:
        result = results_queue.get()
        print("[MANAGER] Result pulled:", result)

        reset_sessions_if_new_day()

        if result["action"] == "trade_result":
            session = result["session"]
            updated_balance = result.get("balance", 0.0)

            # Save the finished session
            ALL_SESSIONS.append(session)

            notify_trade_result(session, updated_balance)

            check_and_notify_report(session)

        elif result["action"] == "balance":
            notify_balance(result["balance"])

        else:
            print("[MANAGER] Unknown result type:", result)