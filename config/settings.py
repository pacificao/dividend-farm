# config/settings.py

import os
from pathlib import Path
from dotenv import load_dotenv

# Base project directory (root of the repo)
BASE_DIR = Path(__file__).resolve().parent.parent

# Path to the .env file inside the config directory
ENV_PATH = BASE_DIR / "config" / ".env"

# Load .env if it exists
if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH)
else:
    print(f"[!] Warning: .env file not found at {ENV_PATH}. Using default environment variables.")

# Robinhood credentials
ROBINHOOD_USERNAME = os.getenv("ROBINHOOD_USERNAME")
ROBINHOOD_PASSWORD = os.getenv("ROBINHOOD_PASSWORD")

# Polygon API Key
POLYGON_API_KEY = os.getenv("POLYGON_API_KEY")
if not POLYGON_API_KEY:
    print("[!] POLYGON_API_KEY not set. Please check your config/.env file.")

# Paths for data cache files
CACHE_FILE = BASE_DIR / "data" / "warehouse" / "dividend_cache.csv"
IGNORE_CACHE_FILE = BASE_DIR / "data" / "warehouse" / "ignore_cache.csv"