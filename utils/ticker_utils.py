from typing import Dict, Any


def should_filter_ticker(ticker: str, info: Dict[str, Any]) -> bool:
    """
    Determines if a ticker should be excluded based on suffixes and financial data.
    - 'F': foreign stocks
    - 'Y': ADRs
    - 'Q': bankrupt or distressed companies

    Parameters:
        ticker (str): The stock ticker symbol.
        info (dict): Financial metadata from yfinance.

    Returns:
        bool: True if the ticker should be excluded, False otherwise.
    """
    ticker = ticker.upper()

    if ticker.endswith("F") or (len(ticker) == 5 and ticker.endswith("Y")):
        return True

    if ticker.endswith("Q"):
        if info.get("financialCurrency") is None or info.get("regularMarketPrice") is None:
            return True
        if info.get("marketCap", 0) <= 0:
            return True
        if info.get("quoteType") == "NONE":
            return True

    return False


def is_tradable_on_robinhood(ticker: str, robinhood_client) -> bool:
    """
    Checks if a ticker is available for trading on Robinhood.

    Parameters:
        ticker (str): The stock ticker symbol.
        robinhood_client: The authenticated robin_stocks.robinhood client.

    Returns:
        bool: True if tradable, False if not found or API error occurs.
    """
    try:
        result = robinhood_client.stocks.find_instrument_data(ticker)
        return bool(result)
    except Exception:
        return False


def is_valid_ticker(ticker: str, exclude_f: bool, exclude_y: bool, exclude_q: bool) -> bool:
    """
    Basic string-based validation for filtering ticker suffixes.

    Parameters:
        ticker (str): The stock ticker symbol.
        exclude_f (bool): Exclude tickers ending in 'F'.
        exclude_y (bool): Exclude tickers ending in 'Y'.
        exclude_q (bool): Exclude tickers ending in 'Q'.

    Returns:
        bool: True if ticker passes all filters, False otherwise.
    """
    ticker = ticker.upper()

    if exclude_f and ticker.endswith("F"):
        return False
    if exclude_y and (len(ticker) == 5 and ticker.endswith("Y")):
        return False
    if exclude_q and ticker.endswith("Q"):
        return False

    return True