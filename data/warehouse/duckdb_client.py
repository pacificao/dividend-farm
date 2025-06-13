import duckdb
from pathlib import Path

# Define DuckDB file path (modify if using centralized data directory)
DB_PATH = Path(__file__).resolve().parent.parent / "storage" / "dividend_data.duckdb"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

# Establish connection
conn = duckdb.connect(str(DB_PATH))

def create_tables():
    """
    Initializes required tables if they don't already exist.
    """
    conn.execute("""
        CREATE TABLE IF NOT EXISTS dividends (
            ticker TEXT,
            ex_dividend_date DATE,
            dividend_amount DOUBLE,
            stock_price DOUBLE,
            dividend_yield DOUBLE,
            company TEXT,
            source TEXT,
            fetched_at TIMESTAMP
        );
    """)

def insert_dividend_data(df, source="polygon"):
    """
    Inserts dividend data from a DataFrame into DuckDB.
    """
    df["source"] = source
    df["fetched_at"] = pd.Timestamp.now()
    conn.register("incoming_data", df)
    conn.execute("""
        INSERT INTO dividends
        SELECT * FROM incoming_data;
    """)
    conn.unregister("incoming_data")

def query_dividends(min_yield=0.0, days_ahead=14):
    """
    Queries upcoming dividends meeting criteria.
    """
    query = f"""
        SELECT * FROM dividends
        WHERE dividend_yield >= {min_yield}
        AND ex_dividend_date BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '{days_ahead} days'
        ORDER BY dividend_yield DESC
    """
    return conn.execute(query).df()