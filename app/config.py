from pathlib import Path

# Dynamically resolve the project root based on the current file location
BASE_DIR = Path(__file__).resolve().parent

# Define data folder and files
DATA_DIR = BASE_DIR / "data"
CACHE_FILE = DATA_DIR / "dividend_cache.csv"
IGNORE_CACHE_FILE = DATA_DIR / "ignore_cache.csv"

# Create the folder if it doesn't exist
DATA_DIR.mkdir(parents=True, exist_ok=True)