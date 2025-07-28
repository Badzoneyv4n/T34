from datetime import datetime, timedelta
from bot.utils.session import SignalSession
from pocketoptionapi.stable_api import PocketOption
from bot.utils.scheduler import execute_signal
import pytz, time, os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

user_timezone = os.getenv("TZ", '')  # fallback if missing
if user_timezone == '':
    raise ValueError("Please set your timezone in .env file as TZ=Your/Timezone")

api = PocketOption("your_ssid_here", True)  # Replace with your actual SSID and demo mode
tz = pytz.timezone(user_timezone)
fake_now = datetime.now(tz)



# 🧪 Fake session
session = SignalSession(
    pair="USDJPY_otc",
    expiration=60,
    direction="call",
    entry_time=fake_now + timedelta(seconds=5),
    martingale_levels=[
        fake_now + timedelta(seconds=70),
        fake_now + timedelta(seconds=140),
    ],
    initial_amount=100.0
)

for i in range(3):
    
    time.sleep(4)  # Simulate waiting for the next level

    # ⚙️ Run simulation
    profit, final_balance = execute_signal(session, api, balance=1000.0,)

    print(f"Simulated profit: {profit}")
    print(f"Final balance: {final_balance}")
