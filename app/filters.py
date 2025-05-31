import pandas as pd
from utils.ticker_utils import is_valid_ticker

def apply_filters(
    df: pd.DataFrame,
    min_yield: float = 0.0,
    exclude_f: bool = True,
    exclude_y: bool = True,
    exclude_q: bool = True
) -> pd.DataFrame:
    """
    Apply filtering rules to a DataFrame of dividend stocks.

    Parameters:
        df (pd.DataFrame): Input DataFrame with dividend data.
        min_yield (float): Minimum dividend yield to include.
        exclude_f (bool): Exclude tickers ending in 'F' (foreign).
        exclude_y (bool): Exclude tickers ending in 'Y' (ADR).
        exclude_q (bool): Exclude tickers ending in 'Q' (distressed).

    Returns:
        pd.DataFrame: Filtered DataFrame.
    """
    df = df.copy()
    df["Dividend Yield"] = pd.to_numeric(df["Dividend Yield"], errors="coerce")
    df = df[df["Dividend Yield"] >= min_yield]
    df = df[df["Ticker"].apply(lambda t: is_valid_ticker(t, exclude_f, exclude_y, exclude_q))]
    return df