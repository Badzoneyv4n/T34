# bot/core/parser.py

import re
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def parse_signal(message: str) -> dict:
    """
    Parses a trading signal message and extracts relevant information.

    Args:
        message (str): The message containing the trading signal.

    Returns:
        dict: A dictionary containing the parsed signal information.
    """

    pair_pattern = r"[A-Z]{3}/[A-Z]{3}"
    expiration_pattern = r"Expiration[^\d]*\*{0,2}([0-9]+M)\*{0,2}"
    entry_pattern = r"Entry\s*(?:at|@)?[^\d]*\*{0,2}([0-9:]+)\*{0,2}"
    direction_pattern = r"\b(BUY|SELL)\b"
    martingale_pattern = r"level at\s+([0-9:]+)"

    pair_match = re.search(pair_pattern, message)
    pair = pair_match.group(0) if pair_match else None
    if pair and "OTC" in message.upper():
        pair += " OTC"

    expiration_match = re.search(expiration_pattern, message, re.IGNORECASE)
    entry_match = re.search(entry_pattern, message, re.IGNORECASE)
    direction_match = re.search(direction_pattern, message, re.IGNORECASE)
    martingale_matches = re.findall(martingale_pattern, message, re.IGNORECASE)

    return {
        "pair": pair,
        "expiration": expiration_match.group(1) if expiration_match else None,
        "entry_time": entry_match.group(1) if entry_match else None,
        "direction": direction_match.group(1) if direction_match else None,
        "martingale_levels": martingale_matches
    }