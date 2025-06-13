# core/filters.py

import pandas as pd
from utils.ticker_utils import is_valid_ticker, is_probably_otc_ticker


def apply_filters(df, min_yield=0.0, exclude_f=True, exclude_y=True, exclude_q=True, strict_filtering=True):
    """
    Filters a dividend DataFrame based on yield, ticker format, and risk factors.

    Args:
        df (pd.DataFrame): The input DataFrame.
        min_yield (float): Minimum dividend yield to include.
        exclude_f (bool): Exclude tickers ending in .F or 5-letter foreign suffixes.
        exclude_y (bool): Exclude tickers ending in .Y or 5-letter ADR suffixes.
        exclude_q (bool): Exclude tickers ending in .Q or bankruptcy suffixes.
        strict_filtering (bool): Exclude penny stocks and extreme yields.

    Returns:
        pd.DataFrame: Filtered DataFrame.
    """
    df = df.copy()

    # Normalize column names
    if "Stock Price" in df.columns and "Price" not in df.columns:
        df.rename(columns={"Stock Price": "Price"}, inplace=True)

    # Normalize data
    df["Ticker"] = df["Ticker"].astype(str).str.strip().str.upper()
    df["Dividend Yield"] = pd.to_numeric(df.get("Dividend Yield", 0), errors="coerce")
    df["Price"] = pd.to_numeric(df.get("Price", 0), errors="coerce")

    # Remove rows missing required data
    df = df.dropna(subset=["Ticker", "Dividend Yield", "Price"])

    # Yield filter
    df = df[df["Dividend Yield"] >= min_yield]

    # Suffix & OTC-style filtering
    df = df[df["Ticker"].apply(
        lambda t: is_valid_ticker(t, exclude_f, exclude_y, exclude_q) and not is_probably_otc_ticker(t)
    )]

    # Strict filtering for penny stocks and unrealistic yields
    if strict_filtering:
        df = df[df["Price"] >= 1.00]
        df = df[df["Dividend Yield"] <= 25.0]

    return df


def should_filter_ticker(ticker: str, info: dict) -> bool:
    """
    Evaluates ticker for OTC status or signs of distress based on metadata.

    Args:
        ticker (str): Ticker symbol.
        info (dict): Ticker metadata from yfinance or similar.

    Returns:
        bool: True if the ticker should be excluded.
    """
    if not is_valid_ticker(ticker):
        return True

    market = info.get("market", "").upper()
    quote_type = info.get("quoteType", "").upper()
    summary = info.get("longBusinessSummary", "").lower()

    if "OTC" in market or "OTC" in quote_type:
        return True
    if "bankrupt" in summary or summary.strip() == "":
        return True
    if is_probably_otc_ticker(ticker):
        return True

    return False