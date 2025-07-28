# bot/utils/utils.py

from datetime import datetime , timedelta
from dotenv import load_dotenv
import pytz, os

# Load environment variables from .env file
load_dotenv()

user_timezone = os.getenv("TZ", '')  # fallback if missing
if user_timezone == '':
    raise ValueError("Please set your timezone in .env file as TZ=Your/Timezone")

def map_pair(pair: str) -> str:
    pair = pair.replace("/", "").replace(" ", "").upper()
    if "OTC" in pair:
        pair = pair.replace("OTC", "") + "_otc"
    else:
        pair = pair + "_otc"  # default to OTC
    return pair

def convert_to_local(entry_time_str: str) -> datetime:
    """
    Convert signal time (HH:MM) in UTC-4 (New York) to local timezone datetime.
    Handles day rollover if signal time is earlier than now.
    """
    ny_tz = pytz.timezone("America/New_York")
    local_tz = pytz.timezone(user_timezone)

    # Get now in NY time
    now_ny = datetime.now(ny_tz)

    # Parse input time for today
    hour, minute = map(int, entry_time_str.split(":"))
    parsed_time = now_ny.replace(hour=hour, minute=minute, second=0, microsecond=0)

    # If the parsed time is already before now by more than ~1 min, roll forward to tomorrow
    if parsed_time < now_ny - timedelta(minutes=1):
        parsed_time += timedelta(days=1)

    # Convert to local TZ
    local_time = parsed_time.astimezone(local_tz)

    return local_time
