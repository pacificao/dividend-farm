#!/bin/bash

APP_DIR="/home/nathan/dividend-ai"
LOG_FILE="$APP_DIR/dividend_farm.log"
VENV_PATH="/home/nathan/.venv"
FILES_TO_WATCH=("app.py" "dividend_bot.py")

source "$VENV_PATH/bin/activate"
cd "$APP_DIR"

echo "$(date): Starting dividend farming app watcher" >> "$LOG_FILE"

run_streamlit() {
  pkill -f "streamlit run app.py"
  echo "$(date): Launching Streamlit app" >> "$LOG_FILE"
  nohup streamlit run app.py >> "$LOG_FILE" 2>&1 &
}

# Initialize baseline checksums
declare -A FILE_HASHES
for FILE in "${FILES_TO_WATCH[@]}"; do
  FILE_HASHES["$FILE"]=$(md5sum "$FILE" | awk '{print $1}')
done

run_streamlit

# Poll for actual content changes every 2 seconds
while true; do
  sleep 2
  for FILE in "${FILES_TO_WATCH[@]}"; do
    NEW_HASH=$(md5sum "$FILE" | awk '{print $1}')
    if [ "${FILE_HASHES["$FILE"]}" != "$NEW_HASH" ]; then
      echo "$(date): Detected content change in $FILE. Restarting app..." >> "$LOG_FILE"
      FILE_HASHES["$FILE"]=$NEW_HASH
      run_streamlit
      break
    fi
  done
done