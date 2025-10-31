Stock Analyzer
===============

A small Streamlit app that fetches market data and highlights top gainers and stocks reporting earnings.

What it does
-----------
- Fetches top gainers using Alpha Vantage.
- Filters gainers without news on the trading day.
- Fetches the earnings calendar and filters companies likely to beat estimates based on past quarters.
- Designed as a simple research helper — not financial advice.

Quick start (local)
-------------------
1. Clone or copy this repository to your machine.
2. Create and activate a Python virtual environment (optional but recommended):

```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Run the app:

```bash
streamlit run app.py
```

5. Open http://localhost:8501 in your browser.

API key (Alpha Vantage)
-----------------------
The app requires an Alpha Vantage API key. Do NOT hard-code keys in `app.py` before publishing.

For local testing you can create a secrets file:

- Create the folder `.streamlit` in the project root.
- Add `.streamlit/secrets.toml` with the following content (example):

```toml
ALPHAVANTAGE_API_KEY = "your_api_key_here"
```

Then in `app.py` the app can use:

```python
import streamlit as st
API_KEY = st.secrets.get("ALPHAVANTAGE_API_KEY")

OR 

You can hardcode API key like I did :) (not recommended for obvious reasons)
```

Deploying to Streamlit Community Cloud (recommended)
---------------------------------------------------
1. Push this repository to GitHub.
2. Go to https://streamlit.io/cloud and sign in with GitHub.
3. Click "New app", pick the repo, branch and `app.py` as the main file.
4. Add the API key under "Secrets" (same key name used in your code).
5. Deploy — Streamlit Cloud will install dependencies from `requirements.txt` and host the app.

Notes
------------------
- This app makes live API calls and thus is affected by Alpha Vantage rate limits. The free tier is limited; the app already waits between requests to reduce throttling.
- This is a demo/research tool only. Do not rely on it for trading decisions.

Files added or edited
---------------------
- `requirements.txt` — lists Python dependencies
- `app.py` — main Streamlit application
- `README.md` — this file

Developed by Aniket Mangalampalli with love!
