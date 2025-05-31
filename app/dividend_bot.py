import os
import datetime
import requests
import yfinance as yf
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv
import robin_stocks.robinhood as r

from config import CACHE_FILE, IGNORE_CACHE_FILE  # NEW: Dynamic paths
from utils.ticker_utils import should_filter_ticker, is_tradable_on_robinhood

# Load environment variables
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

ROBINHOOD_USERNAME = os.getenv("ROBINHOOD_USERNAME")
ROBINHOOD_PASSWORD = os.getenv("ROBINHOOD_PASSWORD")
POLYGON_API_KEY = os.getenv("POLYGON_API_KEY")

# Login to Robinhood
logged_in = False
if ROBINHOOD_USERNAME and ROBINHOOD_PASSWORD:
    try:
        r.login(username=ROBINHOOD_USERNAME, password=ROBINHOOD_PASSWORD)
        logged_in = True
    except Exception as e:
        print(f"[!] Robinhood login failed: {e}")
else:
    print("[!] Robinhood credentials not found in .env")

# Ensure CSV files exist
if not CACHE_FILE.exists():
    CACHE_FILE.write_text("Ticker,Ex-Dividend Date,Dividend Amount,Stock Price,Dividend Yield,Company\n")

if not IGNORE_CACHE_FILE.exists():
    IGNORE_CACHE_FILE.write_text("Ticker,IgnoreUntil\n")

def load_ignore_cache():
    try:
        df = pd.read_csv(IGNORE_CACHE_FILE)
        df["IgnoreUntil"] = pd.to_datetime(df["IgnoreUntil"])
        return df
    except:
        return pd.DataFrame(columns=["Ticker", "IgnoreUntil"])

def add_to_ignore_cache(ticker):
    ignore_until = datetime.datetime.now() + datetime.timedelta(days=30)
    with open(IGNORE_CACHE_FILE, "a") as f:
        f.write(f"{ticker},{ignore_until.date()}\n")

def is_ignored(ticker, cache_df):
    if ticker in cache_df["Ticker"].values:
        ignore_until = cache_df.loc[cache_df["Ticker"] == ticker, "IgnoreUntil"].values[0]
        return pd.Timestamp.now().date() < pd.to_datetime(ignore_until).date()
    return False

def load_existing_cache():
    try:
        return pd.read_csv(CACHE_FILE, parse_dates=["Ex-Dividend Date"])
    except:
        return pd.DataFrame(columns=["Ticker", "Ex-Dividend Date", "Dividend Amount", "Stock Price", "Dividend Yield", "Company"])

def get_upcoming_dividends(days_ahead=14, apply_filters=True):
    today = datetime.date.today()
    end_date = today + datetime.timedelta(days=days_ahead)
    existing_cache = load_existing_cache()

    cached = existing_cache[
        (existing_cache["Ex-Dividend Date"] >= pd.Timestamp(today)) &
        (existing_cache["Ex-Dividend Date"] <= pd.Timestamp(end_date))
    ]

    if not cached.empty:
        print("[+] Returning cached data")
        return cached

    polygon_url = (
        f"https://api.polygon.io/v3/reference/dividends?"
        f"ex_dividend_date.gte={today}&ex_dividend_date.lte={end_date}"
        f"&limit=250&apiKey={POLYGON_API_KEY}"
    )

    try:
        response = requests.get(polygon_url)
        response.raise_for_status()
        data = response.json().get("results", [])
    except Exception as e:
        print(f"[!] Polygon API failed: {e}")
        return pd.DataFrame([])

    ignore_cache = load_ignore_cache()
    new_records = []

    for item in data:
        ticker = item.get("ticker", "").upper()
        amount = item.get("cash_amount", 0)
        ex_date = item.get("ex_dividend_date", "N/A")

        if not ticker or amount == 0 or is_ignored(ticker, ignore_cache):
            continue

        try:
            info = yf.Ticker(ticker).info
            price = info.get("regularMarketPrice", 0)
            name = info.get("shortName", "N/A")

            if apply_filters and should_filter_ticker(ticker, info):
                print(f"[!] Skipping {ticker}: Flagged as OTC or distressed")
                add_to_ignore_cache(ticker)
                continue

            if not price or price <= 0:
                raise ValueError("Invalid price")

            if apply_filters and logged_in and not is_tradable_on_robinhood(ticker):
                print(f"[!] Skipping {ticker}: Not tradable on Robinhood")
                add_to_ignore_cache(ticker)
                continue

            yield_pct = (amount / price) * 100

            record = {
                "Ticker": ticker,
                "Ex-Dividend Date": ex_date,
                "Dividend Amount": amount,
                "Stock Price": round(price, 2),
                "Dividend Yield": round(yield_pct, 2),
                "Company": name
            }

            new_records.append(record)

        except Exception as e:
            print(f"[!] Error for {ticker}: {e}")
            add_to_ignore_cache(ticker)

    df_new = pd.DataFrame(new_records)

    if not df_new.empty:
        df_new.to_csv(CACHE_FILE, mode="a", header=False, index=False)

    return df_new