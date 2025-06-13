import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables
dotenv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../config/.env'))
load_dotenv(dotenv_path)

PG_DATABASE = os.getenv("PG_DATABASE")
PG_USER = os.getenv("PG_USER")
PG_PASSWORD = os.getenv("PG_PASSWORD")
PG_HOST = os.getenv("PG_HOST", "localhost")
PG_PORT = os.getenv("PG_PORT", 5432)

def drop_table():
    try:
        conn = psycopg2.connect(
            dbname=PG_DATABASE,
            user=PG_USER,
            password=PG_PASSWORD,
            host=PG_HOST,
            port=PG_PORT
        )
        cur = conn.cursor()
        cur.execute("DROP TABLE IF EXISTS dividends;")
        conn.commit()
        conn.close()
        print("✅ Dropped 'dividends' table successfully.")
    except Exception as e:
        print(f"❌ Failed to drop table: {e}")

if __name__ == "__main__":
    drop_table()