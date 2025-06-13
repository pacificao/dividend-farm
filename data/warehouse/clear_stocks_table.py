# clear_stocks_table.py
import psycopg2
from dotenv import load_dotenv
import os

# Load .env file
load_dotenv(dotenv_path=os.path.abspath("../../config/.env"))

# Get DB credentials from .env
PG_HOST = os.getenv("PG_HOST")
PG_PORT = os.getenv("PG_PORT")
PG_DATABASE = os.getenv("PG_DATABASE")
PG_USER = os.getenv("PG_USER")
PG_PASSWORD = os.getenv("PG_PASSWORD")

# Connect and delete all rows
try:
    conn = psycopg2.connect(
        host=PG_HOST,
        port=int(PG_PORT),
        dbname=PG_DATABASE,
        user=PG_USER,
        password=PG_PASSWORD
    )
    cur = conn.cursor()
    cur.execute("DELETE FROM stocks;")
    conn.commit()
    cur.close()
    conn.close()
    print("✅ All rows deleted from 'stocks' table.")
except Exception as e:
    print(f"❌ Error clearing table: {e}")