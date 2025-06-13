import pandas as pd
from db.db import connect_db


def load_filtered_dividends(min_yield: float, days_ahead: int = 30) -> pd.DataFrame:
    """
    Load upcoming dividend events along with investment scores and grades,
    filtered by minimum yield and number of days ahead.

    Args:
        min_yield (float): Minimum dividend yield to include.
        days_ahead (int): Number of days ahead from today to include.

    Returns:
        pd.DataFrame: Filtered results including ticker info, dividend, score, and grade.
    """
    query = """
        SELECT 
            t.symbol AS "Symbol",
            t.company_name AS "Company",
            d.ex_date AS "Ex-Dividend Date",
            d.amount AS "Dividend Amount",
            d.yield AS "Dividend Yield",
            s.score AS "Score",
            s.grade AS "Grade"
        FROM dividends d
        JOIN tickers t ON d.ticker_id = t.id
        LEFT JOIN investment_scores s 
            ON s.ticker_id = d.ticker_id AND s.ex_date = d.ex_date
        WHERE 
            d.ex_date BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL %s
            AND d.yield IS NOT NULL AND d.yield >= %s
        ORDER BY d.ex_date ASC;
    """

    conn, cursor = None, None
    try:
        conn, cursor = connect_db()
        interval = f"{days_ahead} days"
        cursor.execute(query, (interval, min_yield))
        rows = cursor.fetchall()

        if not rows:
            print(f"[~] No dividends found for yield >= {min_yield}% within {days_ahead} days.")
            return pd.DataFrame()

        return pd.DataFrame(rows)

    except Exception as e:
        print(f"[!] Error in load_filtered_dividends: {e}")
        return pd.DataFrame()

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()