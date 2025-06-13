import re

EXCLUDED_SUFFIXES = {
    "F": ".F",  # Foreign
    "Y": ".Y",  # ADR
    "Q": ".Q",  # Bankruptcy
}

OTC_SUFFIXES = {"F", "Q", "Y", "Z"}  # OTC-style risk indicators


def is_valid_ticker(ticker: str, exclude_f=True, exclude_y=True, exclude_q=True) -> bool:
    """
    Validates a ticker symbol by structure and optional suffix exclusion.

    Args:
        ticker (str): The ticker symbol.
        exclude_f (bool): Exclude tickers with .F suffix (foreign).
        exclude_y (bool): Exclude tickers with .Y suffix (ADR).
        exclude_q (bool): Exclude tickers with .Q suffix (bankruptcy).

    Returns:
        bool: True if the ticker is structurally valid and not excluded.
    """
    if not isinstance(ticker, str):
        return False

    ticker = ticker.strip().upper()

    if exclude_f and ticker.endswith(EXCLUDED_SUFFIXES["F"]):
        return False
    if exclude_y and ticker.endswith(EXCLUDED_SUFFIXES["Y"]):
        return False
    if exclude_q and ticker.endswith(EXCLUDED_SUFFIXES["Q"]):
        return False

    # Allow up to 5 letters, optionally followed by a period and one letter (e.g., BRK.B)
    return bool(re.fullmatch(r'^[A-Z]{1,5}(\.[A-Z])?$', ticker))


def is_probably_otc_ticker(ticker: str) -> bool:
    """
    Heuristically flags tickers that are *likely* OTC or distressed.
    - Matches 5-letter tickers ending in F, Q, Z, or Y (e.g., SIXGF, CNFRZ).

    Args:
        ticker (str): The ticker to evaluate.

    Returns:
        bool: True if the ticker appears to be OTC-style.
    """
    ticker = ticker.strip().upper()

    return (
        len(ticker) == 5 and
        ticker[-1] in OTC_SUFFIXES and
        "." not in ticker
    )


def is_otc_or_distressed(ticker_info: dict) -> bool:
    """
    Uses metadata from sources like yfinance to determine distress or OTC flags.

    Args:
        ticker_info (dict): Dictionary with ticker metadata.

    Returns:
        bool: True if the stock is OTC or appears distressed.
    """
    exchange = ticker_info.get("exchange", "").upper()
    price = ticker_info.get("regularMarketPrice", 0)

    if "OTC" in exchange or "PINK" in exchange:
        return True

    try:
        price = float(price)
        if price < 1.00:
            return True
    except (ValueError, TypeError):
        return True

    return False