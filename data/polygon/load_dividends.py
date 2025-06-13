import os
import time
from datetime import datetime, timedelta
import requests
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv

# Load environment variables
dotenv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../config/.env'))
load_dotenv(dotenv_path)
print(f"✅ Loaded .env from {dotenv_path}")

# Get credentials and API key
PG_DATABASE = os.getenv("PG_DATABASE")
PG_USER = os.getenv("PG_USER")
PG_PASSWORD = os.getenv("PG_PASSWORD")
PG_HOST = os.getenv("PG_HOST", "localhost")
PG_PORT = os.getenv("PG_PORT", 5432)
POLYGON_API_KEY = os.getenv("POLYGON_API_KEY")

print(f"🔍 PG_DATABASE = {PG_DATABASE}, POLYGON_API_KEY = {'✓' if POLYGON_API_KEY else '✗'}")

FIELDS = [
    "id", "ticker", "declaration_date", "ex_dividend_date", "payment_date", "record_date",
    "cash_amount", "currency", "frequency", "dividend_type", "payable_date"
]

REQUIRED_SCHEMA = {
    "id": "text",
    "ticker": "text",
    "declaration_date": "date",
    "ex_dividend_date": "date",
    "payment_date": "date",
    "record_date": "date",
    "cash_amount": "numeric",
    "currency": "text",
    "frequency": "text",
    "dividend_type": "text",
    "payable_date": "date"
}

def ensure_table():
    try:
        conn = psycopg2.connect(
            dbname=PG_DATABASE,
            user=PG_USER,
            password=PG_PASSWORD,
            host=PG_HOST,
            port=PG_PORT
        )
        cur = conn.cursor()

        # Check if table exists
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'dividends'
            );
        """)
        exists = cur.fetchone()[0]

        if exists:
            cur.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'dividends';
            """)
            existing_schema = {row[0]: row[1] for row in cur.fetchall()}
            for col, expected_type in REQUIRED_SCHEMA.items():
                actual_type = existing_schema.get(col)
                if actual_type != expected_type:
                    raise Exception(f"Schema mismatch on column '{col}': expected '{expected_type}', found '{actual_type}'")
            print("🧱 Table 'dividends' already exists with valid schema.")
        else:
            cur.execute("""
                CREATE TABLE dividends (
                    id TEXT PRIMARY KEY,
                    ticker TEXT,
                    declaration_date DATE,
                    ex_dividend_date DATE,
                    payment_date DATE,
                    record_date DATE,
                    cash_amount NUMERIC,
                    currency TEXT,
                    frequency TEXT,
                    dividend_type TEXT,
                    payable_date DATE
                );
            """)
            conn.commit()
            print("🧱 Table 'dividends' created.")

        conn.close()
    except Exception as e:
        print(f"❌ Failed schema check or creation: {e}")
        raise SystemExit("⛔ Aborting due to table schema issue.")

def fetch_all_dividends():
    today = datetime.utcnow().date()
    three_years_ago = today - timedelta(days=3 * 365)
    url = "https://api.polygon.io/v3/reference/dividends"
    params = {
        "apiKey": POLYGON_API_KEY,
        "order": "asc",
        "limit": 1000,
        "ex_dividend_date.gte": str(three_years_ago)
    }

    all_dividends = []
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
            results = data.get("results", [])
            all_dividends.extend(results)
            print(f"[Progress] Downloaded {len(all_dividends)} dividends so far...")

            next_url = data.get("next_url")
            if not next_url:
                break

            time.sleep(13)

            url = "https://api.polygon.io/v3/reference/dividends"
            cursor = next_url.split("cursor=")[-1].split("&")[0]
            params = {
                "apiKey": POLYGON_API_KEY,
                "order": "asc",
                "limit": 1000,
                "cursor": cursor,
                "ex_dividend_date.gte": str(three_years_ago)
            }
            print("🌐 Fetching next page...")

        except requests.exceptions.RequestException as e:
            print(f"❌ Error during fetch: {e}")
            break

    print(f"📦 Total dividends fetched: {len(all_dividends)}")
    return all_dividends

def upsert_dividends(dividends):
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
    for d in dividends:
        dividend_id = d.get("id")
        if dividend_id in seen:
            continue
        seen.add(dividend_id)
        values.append(tuple(d.get(field, None) for field in FIELDS))

    execute_values(
        cur,
        f"""
        INSERT INTO dividends ({', '.join(FIELDS)})
        VALUES %s
        ON CONFLICT (id) DO UPDATE SET
        {', '.join([f"{field} = EXCLUDED.{field}" for field in FIELDS if field != "id"])};
        """,
        values
    )
    conn.commit()
    conn.close()
    print(f"✅ Upserted {len(values)} dividends into the database.")

if __name__ == "__main__":
    ensure_table()
    dividends = fetch_all_dividends()
    upsert_dividends(dividends)