import os
import sys
import traceback
from datetime import datetime, timedelta
import requests
import yfinance as yf
import pandas as pd
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from db.db import (
    connect_db,
    upsert_ticker,
    insert_daily_price,
    insert_dividend,
    insert_investment_score,
)
from core.filters import should_filter_ticker
from core.robinhood import is_tradable_on_robinhood, logged_in
from utils.ticker_utils import is_probably_otc_ticker
from config.settings import POLYGON_API_KEY


def calculate_score(yield_pct, current_price, ma20, dividend_amount):
    if not all([yield_pct, current_price, ma20, dividend_amount]):
        return 0, "F"

    score = 0
    score += min(yield_pct * 2, 40)  # max 40 from yield

    recovery_ratio = (ma20 - (current_price - dividend_amount)) / ma20
    score += max(0, min(recovery_ratio * 100, 40))  # max 40 from expected recovery

    if abs(current_price - ma20) <= 0.02 * current_price:
        score += 10  # bonus for stability

    score = round(min(score, 100), 2)

    if score >= 90: return score, "A+"
    if score >= 80: return score, "A"
    if score >= 70: return score, "B"
    if score >= 60: return score, "C"
    if score >= 50: return score, "D"
    return score, "F"


def safe_cast(val):
    try:
        return None if pd.isna(val) else float(val)
    except:
        return None


def fetch_and_store(symbol, conn, cursor):
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        name = info.get("shortName", "N/A")
        print(f"[+] Processing {symbol} - {name}")
        ticker_id = upsert_ticker(cursor, symbol, name)

        hist = ticker.history(period="30d")
        if hist.empty:
            print(f"[!] No price history for {symbol}")
            return

        hist["ma_5"] = hist["Close"].rolling(window=5).mean()
        hist["ma_20"] = hist["Close"].rolling(window=20).mean()
        latest = hist.dropna().iloc[-1]  # Most recent data

        latest_close = safe_cast(latest.get("Close"))
        latest_ma20 = safe_cast(latest.get("ma_20"))

        # Insert daily history
        for date, row in hist.iterrows():
            insert_daily_price(
                cursor,
                ticker_id,
                date.date(),
                safe_cast(row.get("Close")),
                None,
                safe_cast(row.get("ma_5")),
                safe_cast(row.get("ma_20")),
            )

        # Insert upcoming dividends
        dividends = ticker.dividends
        if dividends.empty:
            print(f"[!] No dividends for {symbol}")
            return

        for ex_date, amount in dividends.items():
            ex_date = ex_date.date()
            dividend_amt = safe_cast(amount)
            if not dividend_amt:
                continue

            yield_pct = round((dividend_amt / latest_close) * 100, 2) if latest_close else None
            score, grade = calculate_score(yield_pct, latest_close, latest_ma20, dividend_amt)

            insert_dividend(
                cursor,
                ticker_id,
                ex_date,
                amount=dividend_amt,
                declared_date=None,
                payment_date=None,
                yield_pct=yield_pct,
            )
            insert_investment_score(cursor, ticker_id, ex_date, score, grade)
            print(f"[~] Score for {symbol} on {ex_date}: {score}, Grade: {grade}")

        conn.commit()

    except Exception as e:
        print(f"[!] Error processing {symbol}: {e}")
        traceback.print_exc()
        conn.rollback()


if __name__ == "__main__":
    load_dotenv(dotenv_path="config/.env")

    today = datetime.today().date()
    end = today + timedelta(days=30)

    conn, cursor = None, None
    try:
        print("[*] Fetching dividend tickers from Polygon API...")
        url = (
            f"https://api.polygon.io/v3/reference/dividends?"
            f"ex_dividend_date.gte={today}&ex_dividend_date.lte={end}"
            f"&limit=250&apiKey={POLYGON_API_KEY.strip()}"
        )
        response = requests.get(url)
        response.raise_for_status()
        data = response.json().get("results", [])
        print(f"[+] Found {len(data)} raw tickers")

        conn, cursor = connect_db()
        tickers = set()

        for item in data:
            ticker = item.get("ticker", "").upper()
            if not ticker or is_probably_otc_ticker(ticker):
                continue
            try:
                yf_info = yf.Ticker(ticker).info
            except:
                continue
            if should_filter_ticker(ticker, yf_info):
                continue
            if logged_in and not is_tradable_on_robinhood(ticker):
                continue
            tickers.add(ticker)

        print(f"[+] Running pipeline for {len(tickers)} filtered tickers...")
        for t in sorted(tickers):
            fetch_and_store(t, conn, cursor)

    finally:
        if cursor: cursor.close()
        if conn: conn.close()