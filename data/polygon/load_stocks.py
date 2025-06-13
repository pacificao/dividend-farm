import os
import time
import requests
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv

# Load environment variables
dotenv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../config/.env'))
load_dotenv(dotenv_path)
print(f"✅ Loaded .env from {dotenv_path}")

# Get database credentials and API key
PG_DATABASE = os.getenv("PG_DATABASE")
PG_USER = os.getenv("PG_USER")
PG_PASSWORD = os.getenv("PG_PASSWORD")
PG_HOST = os.getenv("PG_HOST", "localhost")
PG_PORT = os.getenv("PG_PORT", 5432)
POLYGON_API_KEY = os.getenv("POLYGON_API_KEY")

print(f"🔍 PG_DATABASE = {PG_DATABASE}, POLYGON_API_KEY = {'✓' if POLYGON_API_KEY else '✗'}")

# Define the stock fields to be stored
FIELDS = [
    "ticker", "name", "market", "locale", "primary_exchange", "type",
    "active", "currency_name", "cik", "composite_figi", "share_class_figi",
    "delisted_utc", "last_updated_utc"
]

# Create or update the stocks table with all fields
def ensure_table():
    conn = psycopg2.connect(
        dbname=PG_DATABASE,
        user=PG_USER,
        password=PG_PASSWORD,
        host=PG_HOST,
        port=PG_PORT
    )
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS stocks (
            ticker TEXT PRIMARY KEY,
            name TEXT,
            market TEXT,
            locale TEXT,
            primary_exchange TEXT,
            type TEXT,
            active BOOLEAN,
            currency_name TEXT,
            cik TEXT,
            composite_figi TEXT,
            share_class_figi TEXT,
            delisted_utc TEXT,
            last_updated_utc TEXT
        );
    """)
    conn.commit()
    conn.close()
    print("🧱 Table 'stocks' ensured.")

# Fetch all tickers from Polygon with CS type filter
def fetch_all_tickers():
    url = "https://api.polygon.io/v3/reference/tickers"
    params = {
        "apiKey": POLYGON_API_KEY,
        "type": "CS",               # ✅ Re-added CS filter
        "market": "stocks",
        "order": "asc",
        "sort": "ticker",
        "limit": 1000
    }

    all_tickers = []
    print("🌐 Fetching first page...")

    while True:
        try:
            response = requests.get(url, params=params)
            if response.status_code == 429:
                print("⏳ Rate limited. Sleeping for 60 seconds...")
                time.sleep(60)
                continue

            response.raise_for_status()
            data = response.json()

            tickers = data.get("results", [])
            all_tickers.extend(tickers)
            print(f"[Progress] Downloaded {len(all_tickers)} tickers so far...")

            next_url = data.get("next_url")
            if not next_url:
                break

            # Respect rate limits
            time.sleep(13)

            # Extract cursor from next_url and rebuild URL
            url = "https://api.polygon.io/v3/reference/tickers"
            next_cursor = next_url.split("cursor=")[-1].split("&")[0]
            params = {
                "apiKey": POLYGON_API_KEY,
                "type": "CS",               # ✅ CS still applies to next page
                "market": "stocks",
                "order": "asc",
                "sort": "ticker",
                "limit": 1000,
                "cursor": next_cursor
            }
            print("🌐 Fetching next page...")

        except requests.exceptions.RequestException as e:
            print(f"❌ Error during fetch: {e}")
            break

    print(f"📦 Total tickers fetched: {len(all_tickers)}")
    return all_tickers

# Upsert tickers into the database
def upsert_stocks(tickers):
    conn = psycopg2.connect(
        dbname=PG_DATABASE,
        user=PG_USER,
        password=PG_PASSWORD,
        host=PG_HOST,
        port=PG_PORT
    )
    cur = conn.cursor()

    values = []
    seen = set()
    for t in tickers:
        ticker_symbol = t.get("ticker")
        if ticker_symbol in seen:
            continue
        seen.add(ticker_symbol)
        values.append(tuple(t.get(field, None) for field in FIELDS))

    execute_values(
        cur,
        f"""
        INSERT INTO stocks ({', '.join(FIELDS)})
        VALUES %s
        ON CONFLICT (ticker) DO UPDATE SET
        {', '.join([f"{field} = EXCLUDED.{field}" for field in FIELDS if field != "ticker"])};
        """,
        values
    )
    conn.commit()
    conn.close()
    print(f"✅ Upserted {len(values)} tickers into the database.")

if __name__ == "__main__":
    ensure_table()
    tickers = fetch_all_tickers()
    upsert_stocks(tickers)