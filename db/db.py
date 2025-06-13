import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
from dotenv import load_dotenv

# -------------------------------------------------
# Load Environment Variables
# -------------------------------------------------
load_dotenv()

DB_CONFIG = {
    "dbname": os.getenv("PG_DATABASE"),
    "user": os.getenv("PG_USER"),
    "password": os.getenv("PG_PASSWORD"),
    "host": os.getenv("PG_HOST", "localhost"),
    "port": int(os.getenv("PG_PORT", 5432)),
}

# -------------------------------------------------
# Connection Utilities
# -------------------------------------------------

def get_connection():
    """Create and return a new PostgreSQL database connection."""
    try:
        return psycopg2.connect(**DB_CONFIG)
    except Exception as e:
        print(f"[!] Failed to connect to database: {e}")
        raise

def get_cursor(conn, dict_cursor=False):
    """
    Return a database cursor.
    Args:
        conn: psycopg2 connection
        dict_cursor (bool): Whether to return a RealDictCursor
    """
    try:
        return conn.cursor(cursor_factory=RealDictCursor) if dict_cursor else conn.cursor()
    except Exception as e:
        print(f"[!] Failed to create cursor: {e}")
        raise

def connect_db():
    """
    Convenience function to get both connection and cursor.
    Returns:
        tuple: (connection, cursor)
    """
    conn = get_connection()
    return conn, get_cursor(conn)

# -------------------------------------------------
# Data Insert / Upsert Methods
# -------------------------------------------------

def upsert_ticker(cursor, symbol, name, sector="Unknown"):
    """
    Insert or update a ticker in the tickers table.
    Returns:
        int: ID of the ticker
    """
    cursor.execute("""
        INSERT INTO tickers (symbol, company_name, sector)
        VALUES (%s, %s, %s)
        ON CONFLICT (symbol) DO UPDATE SET
            company_name = EXCLUDED.company_name,
            sector = EXCLUDED.sector
        RETURNING id;
    """, (symbol, name, sector))
    return cursor.fetchone()[0]

def insert_daily_price(cursor, ticker_id, date, price, yield_pct, ma_5, ma_20):
    """
    Insert price and moving average data into ticker_daily.
    """
    cursor.execute("""
        INSERT INTO ticker_daily (
            ticker_id, date, price, dividend_yield, moving_avg_5, moving_avg_20
        ) VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT DO NOTHING;
    """, (ticker_id, date, price, yield_pct, ma_5, ma_20))

def insert_dividend(cursor, ticker_id, ex_date, amount, declared_date=None, payment_date=None, yield_pct=None):
    """
    Insert dividend record into the dividends table.
    """
    cursor.execute("""
        INSERT INTO dividends (
            ticker_id, ex_date, amount, declared_date, payment_date, yield
        ) VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (ticker_id, ex_date) DO UPDATE SET
            amount = EXCLUDED.amount,
            declared_date = COALESCE(EXCLUDED.declared_date, dividends.declared_date),
            payment_date = COALESCE(EXCLUDED.payment_date, dividends.payment_date),
            yield = COALESCE(EXCLUDED.yield, dividends.yield);
    """, (ticker_id, ex_date, amount, declared_date, payment_date, yield_pct))

def insert_investment_score(cursor, ticker_id, ex_date, score, grade, calculated_at=None):
    """
    Insert or update investment score and grade in investment_scores.
    """
    calculated_at = calculated_at or datetime.utcnow()
    cursor.execute("""
        INSERT INTO investment_scores (
            ticker_id, ex_date, score, grade, calculated_at
        ) VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (ticker_id, ex_date) DO UPDATE SET
            score = EXCLUDED.score,
            grade = EXCLUDED.grade,
            calculated_at = EXCLUDED.calculated_at;
    """, (ticker_id, ex_date, score, grade, calculated_at))