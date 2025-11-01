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
- Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml`
- Add your API key:

```toml
ALPHAVANTAGE_API_KEY = "your_api_key_here"
```

The app automatically reads from `st.secrets` or environment variables.

Deploying to Render.com or Streamlit Cloud
-------------------------------------------
**Option 1: Render.com (Recommended)**
1. Push this repository to GitHub.
2. Go to https://render.com and sign in with GitHub.
3. Click "New +" → "Web Service".
4. Connect your repository.
5. Render will auto-detect the `render.yaml` configuration.
6. Add environment variable: `ALPHAVANTAGE_API_KEY = "your_key_here"`.
7. Deploy!

**Option 2: Streamlit Community Cloud**
1. Push this repository to GitHub.
2. Go to https://streamlit.io/cloud and sign in with GitHub.
3. Click "New app", pick the repo, branch and `app.py` as the main file.
4. Add the API key under "Secrets".
5. Deploy!

Notes
------------------
- This app makes live API calls and thus is affected by Alpha Vantage rate limits. The free tier is limited; the app already waits between requests to reduce throttling.
- This is a demo/research tool only. Do not rely on it for trading decisions.

Files added or edited
---------------------
- `requirements.txt` — lists Python dependencies
- `app.py` — main Streamlit application
- `render.yaml` — Render.com deployment configuration
- `README.md` — this file

Developed by Aniket Mangalampalli with love!
