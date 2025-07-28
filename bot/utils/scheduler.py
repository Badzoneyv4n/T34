# bot/utils/scheduler.py

import time, os
from datetime import datetime
from dotenv import load_dotenv
import pytz

from bot.utils.notifier import notify_trade_placed
from bot.utils.session import SignalSession, TradeResult , ALL_SESSIONS
from pocketoptionapi.stable_api import PocketOption
from bridge import api_lock

# Load environment variables from .env file
load_dotenv()

user_timezone = os.getenv("TZ", '')  # fallback if missing
if user_timezone == '':
    raise ValueError("Please set your timezone in .env file as TZ=Your/Timezone")

def execute_signal(session: SignalSession, api: PocketOption, balance: float):
    with api_lock:
        amount = session.initial_amount
        updated_balance = None
        
        print(
            f"🚀 Starting execute_signal for pair {session.pair} "
            f"with base amount ${amount} with expiration {session.expiration} sec "
            f"in {session.direction.upper()} direction "
        )

        for level, entry_time in enumerate([session.entry_time] + session.martingale_levels):

            # Always get your local time
            local_tz = pytz.timezone(user_timezone)
            now = datetime.now(local_tz)

            wait_seconds = (entry_time - now).total_seconds() - 2
            print(f"⏳ Waiting for entry time {entry_time} (in {wait_seconds:.2f} seconds)")

            if wait_seconds > 0:
                time.sleep(wait_seconds)

            print(f"📈 Placing trade: level={level+1} amount=${amount:.2f} pair {session.pair} direction {session.direction} expiration {session.expiration} sec")

            success, order_id = api.buy(
                amount=amount,
                active=session.pair,
                action=session.direction,
                expirations=session.expiration
            )

            if not success:
                print(f"❌ Trade failed to place. Skipping martingale. {session.pair} {session.direction} {amount} in {session.expiration} seconds")
                break

            print(f"✅ BUY: success={success}, order_id={order_id}")
            notify_trade_placed(session.pair, entry_time, amount, order_id , session.direction ,  level)

            # Wait for trade to close
            time.sleep(session.expiration + 5)

            profit, result = api.check_win(order_id) or (None, "unknown")
        
            print(f"🏁 Order {order_id} result: {result} with profit {profit}")

            trade = TradeResult(
                entry_time=entry_time,
                level=level,
                amount=amount,
                order_id=order_id,
                result=result,
                profit=profit if profit else -amount
            )
            session.add_trade_result(trade)

            if result == "win":
                print(f"🎉 Trade won! Stopping martingale.")
                updated_balance = api.get_balance()
                break
            else:
                amount *= 2
                print(f"🔄 Trade lost. Next martingale amount: ${amount:.2f}")

        if updated_balance is None:
            updated_balance = api.get_balance()  # If all levels lost, get final balance too!

        print(f"[Scheduler]💰 Final balance : ${updated_balance:.2f}")
        
        # Avoid duplicate session based on entry_time + pair + direction
        for s in ALL_SESSIONS:
            if s.entry_time == session.entry_time and s.pair == session.pair and s.direction == session.direction:
                print(f"[Scheduler]⏭️ Duplicate session for {session.pair} at {session.entry_time}. Skipping add.")
                return session.total_profit, updated_balance

        print(f"[Scheduler]📊 Adding session for pair {session.pair} with total profit ${session.total_profit:.2f}")
        ALL_SESSIONS.append(session)

        return session.total_profit , updated_balance

