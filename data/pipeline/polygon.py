import os
import requests
import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
POLYGON_API_KEY = os.getenv("POLYGON_API_KEY")

def get_upcoming_dividends(days_ahead=14, limit=250):
    """
    Fetch upcoming dividend data from Polygon.io API.

    Args:
        days_ahead (int): How many days ahead to look for dividends.
        limit (int): Max number of results to fetch.

    Returns:
        List of dividend records (or empty list on error).
    """
    today = datetime.date.today()
    end_date = today + datetime.timedelta(days=days_ahead)

    url = (
        f"https://api.polygon.io/v3/reference/dividends"
        f"?ex_dividend_date.gte={today}"
        f"&ex_dividend_date.lte={end_date}"
        f"&limit={limit}"
        f"&apiKey={POLYGON_API_KEY}"
    )

    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json().get("results", [])
    except Exception as e:
        print(f"[!] Polygon API error: {e}")
        return []