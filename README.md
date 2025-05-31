Dividend Farming AI

A lightweight dividend stock scanner that identifies opportunities to buy dividend-paying stocks just before their ex-dividend date. Built with Python, Streamlit, Robinhood API, Polygon.io, and yFinance.

Features:
	•	Scans upcoming dividend events via Polygon.io
	•	Calculates dividend yield using yFinance
	•	Filters out OTC, distressed, and untradable stocks (optional)
	•	Verifies tradability with Robinhood API
	•	Local caching to minimize API calls
	•	Modular logic structure and dynamic filtering
	•	Streamlit UI with interactive controls

⸻

Installation
	1.	Clone the repository:

git clone https://github.com/pacificao/dividend-farm.git
cd dividend-farm
	2.	Set up your .env file:

cp .env.example .env

Then open .env and fill in your credentials:

ROBINHOOD_USERNAME=your_robinhood_username
ROBINHOOD_PASSWORD=your_robinhood_password
POLYGON_API_KEY=your_polygon_api_key
	3.	Install Python dependencies (use a virtual environment):

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

⸻

Running the App

To launch the web app locally:

streamlit run app.py

Then open your browser to: http://localhost:8501

⸻

Optional: Enable Auto-Start on Reboot with systemd
	1.	Create a shell script called run_app.sh:

#!/bin/bash
cd /path/to/dividend-farm
source venv/bin/activate
streamlit run app.py

Make it executable:

chmod +x run_app.sh
	2.	Create a systemd service at /etc/systemd/system/dividend-farm.service:

[Unit]
Description=Dividend Farm Streamlit App
After=network.target

[Service]
User=yourusername
WorkingDirectory=/path/to/dividend-farm
ExecStart=/path/to/dividend-farm/run_app.sh
Restart=always

[Install]
WantedBy=multi-user.target

Then enable and start it:

sudo systemctl daemon-reexec
sudo systemctl enable dividend-farm
sudo systemctl start dividend-farm

⸻

Project Structure

dividend-farm/
├── app.py
├── dividend_bot.py
├── filters.py
├── utils/
│   └── ticker_utils.py
├── .env.example
├── run_app.sh
└── README.md

⸻

Future Plans
	•	UI filter toggles for OTC, distressed, and tradability
	•	Optional buy/sell logic for automated dividend harvesting
	•	Robinhood trade placement (optional)
	•	Postgres and Redis-based data handling
	•	Multi-user accounts and dashboards

⸻

License: MIT
Repo: https://github.com/pacificao/dividend-farm