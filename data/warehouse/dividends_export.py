import os
import psycopg2
import pandas as pd
from dotenv import load_dotenv

# Load .env
env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../config/.env"))
load_dotenv(env_path)

# Connect
conn = psycopg2.connect(
    host=os.getenv("PG_HOST"),
    port=os.getenv("PG_PORT"),
    dbname=os.getenv("PG_DATABASE"),
    user=os.getenv("PG_USER"),
    password=os.getenv("PG_PASSWORD")
)

# Query first 100 rows
query = "SELECT * FROM dividends LIMIT 100000;"
df = pd.read_sql(query, conn)

# Export to Excel
output_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "dividends_export.xlsx"))
df.to_excel(output_path, index=False)

print(f"✅ Exported first 100000 rows to {output_path}")
conn.close()