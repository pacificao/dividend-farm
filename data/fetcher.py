import os
import datetime
import requests
import yfinance as yf
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

POLYGON_API_KEY = os.getenv("POLYGON_API_KEY")

def fetch_dividends_from_polygon(days_ahead=14):
    """
    Fetches upcoming dividend events from Polygon.io API.
    Returns a DataFrame or empty DataFrame on failure.
    """
    today = datetime.date.today()
    end_date = today + datetime.timedelta(days=days_ahead)

    url = (
        f"https://api.polygon.io/v3/reference/dividends?"
        f"ex_dividend_date.gte={today}&ex_dividend_date.lte={end_date}"
        f"&limit=250&apiKey={POLYGON_API_KEY}"
    )

    try:
        response = requests.get(url)
        response.raise_for_status()
        results = response.json().get("results", [])
        return pd.DataFrame(results)
    except Exception as e:
        print(f"[!] Failed to fetch from Polygon: {e}")
        return pd.DataFrame()

def fetch_yfinance_info(ticker: str) -> dict:
    """
    Fetches detailed stock info from Yahoo Finance for a given ticker.
    Returns an info dictionary or empty dict on failure.
    """
    try:
        return yf.Ticker(ticker).info
    except Exception as e:
        print(f"[!] yFinance failed for {ticker}: {e}")
        return {}