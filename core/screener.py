import datetime
import requests
import yfinance as yf
import pandas as pd
from pathlib import Path

from config.settings import CACHE_FILE, IGNORE_CACHE_FILE, POLYGON_API_KEY
from core.filters import should_filter_ticker
from core.robinhood import is_tradable_on_robinhood, logged_in
from utils.ticker_utils import is_probably_otc_ticker

# -------------------------------
# Initialize Cache Files
# -------------------------------

def ensure_cache_files_exist():
    if not CACHE_FILE.exists():
        CACHE_FILE.write_text("Ticker,Ex-Dividend Date,Dividend Amount,Price,Dividend Yield,Company\n")
    if not IGNORE_CACHE_FILE.exists():
        IGNORE_CACHE_FILE.write_text("Ticker,IgnoreUntil\n")

ensure_cache_files_exist()

# -------------------------------
# Ignore Cache Utilities
# -------------------------------

def load_ignore_cache():
    try:
        df = pd.read_csv(IGNORE_CACHE_FILE, parse_dates=["IgnoreUntil"])
        return df
    except Exception:
        return pd.DataFrame(columns=["Ticker", "IgnoreUntil"])

def add_to_ignore_cache(ticker):
    ignore_until = datetime.datetime.now() + datetime.timedelta(days=30)
    with open(IGNORE_CACHE_FILE, "a") as f:
        f.write(f"{ticker},{ignore_until.date()}\n")

def is_ignored(ticker, ignore_df):
    row = ignore_df.loc[ignore_df["Ticker"] == ticker]
    if not row.empty:
        return pd.Timestamp.now().date() < row.iloc[0]["IgnoreUntil"].date()
    return False

# -------------------------------
# Cached Screener Results
# -------------------------------

def load_existing_cache():
    try:
        df = pd.read_csv(CACHE_FILE)
        # Normalize column names and ensure datetime types
        if "Stock Price" in df.columns and "Price" not in df.columns:
            df.rename(columns={"Stock Price": "Price"}, inplace=True)

        df["Ex-Dividend Date"] = pd.to_datetime(df["Ex-Dividend Date"], errors="coerce")
        df.dropna(subset=["Ex-Dividend Date"], inplace=True)
        return df
    except Exception:
        return pd.DataFrame(columns=[
            "Ticker", "Ex-Dividend Date", "Dividend Amount",
            "Price", "Dividend Yield", "Company"
        ])

# -------------------------------
# Main Screener Logic
# -------------------------------

def get_upcoming_dividends(days_ahead=14, strict_filtering=True):
    today = datetime.date.today()
    end_date = today + datetime.timedelta(days=days_ahead)

    cached_df = load_existing_cache()

    cached_result = cached_df[
        (cached_df["Ex-Dividend Date"] >= pd.Timestamp(today)) &
        (cached_df["Ex-Dividend Date"] <= pd.Timestamp(end_date))
    ]

    if not cached_result.empty:
        print("[+] Returning cached dividend data")
        return cached_result

    print("[*] Fetching fresh data from Polygon API")

    polygon_url = (
        f"https://api.polygon.io/v3/reference/dividends?"
        f"ex_dividend_date.gte={today}&ex_dividend_date.lte={end_date}"
        f"&limit=250&apiKey={POLYGON_API_KEY.strip()}"
    )

    try:
        response = requests.get(polygon_url)
        response.raise_for_status()
        polygon_data = response.json().get("results", [])
    except Exception as e:
        print(f"[!] Polygon API error: {e}")
        return pd.DataFrame([])

    ignore_cache = load_ignore_cache()
    new_records = []

    for item in polygon_data:
        ticker = item.get("ticker", "").upper()
        amount = item.get("cash_amount", 0)
        ex_date_str = item.get("ex_dividend_date", None)

        if not ticker or amount <= 0 or not ex_date_str or is_ignored(ticker, ignore_cache):
            continue

        if is_probably_otc_ticker(ticker):
            print(f"[!] Skipping {ticker}: Flagged as OTC/pink")
            add_to_ignore_cache(ticker)
            continue

        try:
            ex_date = pd.to_datetime(ex_date_str, errors="coerce")
            if pd.isna(ex_date):
                raise ValueError("Invalid ex-dividend date")

            info = yf.Ticker(ticker).info
            price = info.get("regularMarketPrice", 0)
            name = info.get("shortName", "N/A")

            if strict_filtering:
                if should_filter_ticker(ticker, info):
                    print(f"[!] Skipping {ticker}: Fails filter")
                    add_to_ignore_cache(ticker)
                    continue

                if logged_in and not is_tradable_on_robinhood(ticker):
                    print(f"[!] Skipping {ticker}: Not tradable on Robinhood")
                    add_to_ignore_cache(ticker)
                    continue

            if not price or price <= 0:
                raise ValueError("Invalid market price")

            dividend_yield = round((amount / price) * 100, 2)

            new_records.append({
                "Ticker": ticker,
                "Ex-Dividend Date": ex_date,
                "Dividend Amount": amount,
                "Price": round(price, 2),
                "Dividend Yield": dividend_yield,
                "Company": name
            })

        except Exception as e:
            print(f"[!] Error processing {ticker}: {e}")
            add_to_ignore_cache(ticker)

    df_new = pd.DataFrame(new_records)

    if not df_new.empty:
        existing = load_existing_cache()
        combined = pd.concat([existing, df_new], ignore_index=True)
        combined.drop_duplicates(subset=["Ticker", "Ex-Dividend Date"], inplace=True)
        combined.to_csv(CACHE_FILE, index=False)

    return df_new