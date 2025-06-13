#!/bin/bash

# Exit on error
set -e

# Set the PYTHONPATH to the project root for consistent imports
export PYTHONPATH=$(pwd)

# Activate virtual environment
source .venv/bin/activate

# Load environment variables from config/.env
ENV_FILE="config/.env"
if [ -f "$ENV_FILE" ]; then
    echo "[+] Loading environment variables from $ENV_FILE"
    # Export each line one-by-one to avoid malformed exports
    while IFS='=' read -r key value; do
        if [[ "$key" =~ ^[A-Za-z_][A-Za-z0-9_]*$ ]]; then
            export "$key=$value"
        fi
    done < <(grep -v '^#' "$ENV_FILE")
else
    echo "[!] Warning: $ENV_FILE not found. Using default environment."
fi

# Just a friendly log
echo "[+] Starting Dividend Farm Streamlit app..."
streamlit run app/main.py