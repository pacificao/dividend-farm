import os
from pathlib import Path
from dotenv import load_dotenv
import robin_stocks.robinhood as r

# Load environment variables
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

ROBINHOOD_USERNAME = os.getenv("ROBINHOOD_USERNAME")
ROBINHOOD_PASSWORD = os.getenv("ROBINHOOD_PASSWORD")

# Global login state
logged_in = False


def login_to_robinhood():
    """
    Attempts to log in to Robinhood using credentials in the .env file.
    Sets `logged_in` to True if successful.
    """
    global logged_in

    if logged_in:
        return True

    if not ROBINHOOD_USERNAME or not ROBINHOOD_PASSWORD:
        print("[!] Robinhood credentials missing in .env file.")
        return False

    try:
        r.login(username=ROBINHOOD_USERNAME, password=ROBINHOOD_PASSWORD)
        logged_in = True
        print("[+] Successfully logged in to Robinhood.")
        return True
    except Exception as e:
        print(f"[!] Robinhood login failed: {e}")
        return False


def is_tradable_on_robinhood(ticker: str) -> bool:
    """
    Checks if a ticker is available for trading on Robinhood.
    Requires a successful login first.
    """
    if not logged_in:
        return False

    try:
        result = r.stocks.find_instrument_data(ticker)
        return bool(result)
    except Exception as e:
        print(f"[!] Error checking tradability for {ticker}: {e}")
        return False