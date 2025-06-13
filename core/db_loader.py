# core/db_loader.py

import pandas as pd
from db import get_connection, get_cursor

def load_filtered_dividends(min_yield: float = 2.5, days_ahead: int = 14) -> pd.DataFrame:
    conn = get_connection()
    cursor = get_cursor(conn)

    query = """
        SELECT
            t.symbol AS Ticker,
            d.ex_date AS "Ex-Dividend Date",
            d.amount AS "Dividend Amount",
            td.price AS Price,
            ROUND((d.amount / td.price) * 100, 2) AS "Dividend Yield",
            t.company_name AS Company
        FROM dividends d
        JOIN tickers t ON t.id = d.ticker_id
        JOIN ticker_daily td ON td.ticker_id = t.id AND td.date = d.ex_date - INTERVAL '1 day'
        WHERE d.ex_date BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL %s DAY
          AND (d.amount / td.price) * 100 >= %s
        ORDER BY "Dividend Yield" DESC
    """
    cursor.execute(query, (days_ahead, min_yield))
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]

    conn.close()
    return pd.DataFrame(rows, columns=columns)