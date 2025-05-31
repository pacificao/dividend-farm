#!/bin/bash

# 1. Update system
echo "[*] Updating system..."
sudo apt update && sudo apt upgrade -y

# 2. Install Ubuntu GUI + RDP server
echo "[*] Installing desktop GUI and RDP..."
sudo apt install -y ubuntu-desktop xrdp

# Enable and start xrdp for remote desktop access
sudo systemctl enable xrdp
sudo systemctl start xrdp

# 3. Install Python and dev tools
echo "[*] Installing Python and developer packages..."
sudo apt install -y python3.12 python3.12-venv python3.12-dev python3-pip git curl

# 4. Create project directory
echo "[*] Creating project folder..."
mkdir -p ~/dividend-ai && cd ~/dividend-ai

# 5. Set up virtual environment
echo "[*] Creating Python virtual environment..."
python3.12 -m venv env
source env/bin/activate

# 6. Install Python dependencies
echo "[*] Installing Python packages..."
pip install --upgrade pip
pip install yfinance pandas numpy streamlit scikit-learn beautifulsoup4 requests ta

# 7. Download source files from GitHub
echo "[*] Downloading app and logic engine..."
curl -O https://raw.githubusercontent.com/pacificao/dividend-ai/main/app.py
curl -O https://raw.githubusercontent.com/pacificao/dividend-ai/main/dividend_bot.py

# 8. Final message
echo "✅ Setup complete!"
echo "To launch the app, run:"
echo "cd ~/dividend-ai && source env/bin/activate && streamlit run app.py"
