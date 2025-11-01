import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
import time
import pytz

# Configuration
API_KEY = "IVCROGUOH0S4GJVS"
BASE_URL = "https://www.alphavantage.co/query"

def get_market_status():
    """Check if market is currently open"""
    eastern = pytz.timezone('US/Eastern')
    now = datetime.now(eastern)
    
    # Market hours: 9:30 AM - 4:00 PM ET, Monday-Friday
    is_weekday = now.weekday() < 5
    market_open = now.time() >= datetime.strptime("09:30", "%H:%M").time()
    market_close = now.time() <= datetime.strptime("16:00", "%H:%M").time()
    
    is_open = is_weekday and market_open and market_close
    
    return {
        'is_open': is_open,
        'current_time': now.strftime('%Y-%m-%d %H:%M:%S %Z'),
        'is_weekday': is_weekday
    }

def fetch_top_gainers():
    """Fetch top gainers using Alpha Vantage TOP_GAINERS_LOSERS endpoint"""
    try:
        params = {
            'function': 'TOP_GAINERS_LOSERS',
            'apikey': API_KEY
        }
        
        response = requests.get(BASE_URL, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        if 'Error Message' in data:
            st.error(f"API Error: {data['Error Message']}")
            return pd.DataFrame(), None
        
        if 'Note' in data:
            st.warning(f"API Rate Limit: {data['Note']}")
            return pd.DataFrame(), None
        
        if 'Information' in data:
            st.warning(f"API Info: {data['Information']}")
            return pd.DataFrame(), None
        
        if 'top_gainers' not in data:
            st.warning("No gainers data available")
            return pd.DataFrame(), None
        
        # Get metadata if available
        metadata = data.get('metadata', None)
        last_updated = data.get('last_updated', 'Unknown')
        
        gainers = data['top_gainers']
        df = pd.DataFrame(gainers)
        
        if not df.empty:
            df = df[['ticker', 'price', 'change_percentage', 'volume']].copy()
            df.columns = ['Symbol', 'Price', 'Change %', 'Volume']
            
            df['Change %'] = df['Change %'].str.rstrip('%').astype(float)
            df['Price'] = df['Price'].astype(float).round(2)
            df['Volume'] = pd.to_numeric(df['Volume'], errors='coerce')
            
            # Filter: Price >= $3 and Change >= 50%
            df = df[(df['Price'] >= 3.0) & (df['Change %'] >= 50.0)]
            df = df.sort_values('Change %', ascending=False)
        
        return df, last_updated
        
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching gainers: {e}")
        return pd.DataFrame(), None
    except Exception as e:
        st.error(f"Unexpected error: {e}")
        return pd.DataFrame(), None

def get_intraday_data(symbol, date_str=None):
    """Get intraday data to verify if stock actually gained today"""
    try:
        params = {
            'function': 'TIME_SERIES_INTRADAY',
            'symbol': symbol,
            'interval': '60min',
            'apikey': API_KEY,
            'outputsize': 'compact'
        }
        
        response = requests.get(BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if 'Error Message' in data or 'Note' in data or 'Information' in data:
            return None
        
        if 'Time Series (60min)' not in data:
            return None
        
        time_series = data['Time Series (60min)']
        
        # Convert to DataFrame
        df = pd.DataFrame.from_dict(time_series, orient='index')
        df.index = pd.to_datetime(df.index)
        df = df.sort_index()
        
        # Get today's date
        if date_str:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        else:
            target_date = datetime.now().date()
        
        # Filter for target date
        df_today = df[df.index.date == target_date]
        
        if not df_today.empty:
            open_price = float(df_today.iloc[0]['1. open'])
            close_price = float(df_today.iloc[-1]['4. close'])
            percent_change = ((close_price - open_price) / open_price) * 100
            
            return {
                'open': open_price,
                'close': close_price,
                'change': percent_change,
                'verified': True
            }
        
        return None
        
    except:
        return None

def get_company_overview(symbol):
    """Get company overview including market cap"""
    try:
        params = {
            'function': 'OVERVIEW',
            'symbol': symbol,
            'apikey': API_KEY
        }
        
        response = requests.get(BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if 'Error Message' in data or 'Note' in data or 'Information' in data:
            return None
        
        market_cap = data.get('MarketCapitalization', '0')
        name = data.get('Name', symbol)
        
        try:
            market_cap_val = float(market_cap) if market_cap else 0
        except:
            market_cap_val = 0
        
        return {
            'name': name,
            'market_cap': market_cap_val,
            'market_cap_millions': market_cap_val / 1_000_000 if market_cap_val > 0 else 0
        }
        
    except:
        return None

def check_news_sentiment(symbol, hours_back=24):
    """Check if stock has recent news"""
    try:
        now = datetime.now()
        past = now - timedelta(hours=hours_back)
        
        time_from = past.strftime("%Y%m%dT%H%M")
        time_to = now.strftime("%Y%m%dT%H%M")
        
        params = {
            'function': 'NEWS_SENTIMENT',
            'tickers': symbol,
            'time_from': time_from,
            'time_to': time_to,
            'limit': 50,
            'apikey': API_KEY
        }
        
        response = requests.get(BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if 'Error Message' in data or 'Note' in data or 'Information' in data:
            return None
        
        if 'feed' in data and len(data['feed']) > 0:
            return len(data['feed'])
        
        return 0
        
    except:
        return None

def filter_gainers_comprehensive(gainers_df, max_stocks=10, check_today=True):
    """Filter gainers by market cap and news"""
    if gainers_df.empty:
        return pd.DataFrame()
    
    gainers_df_limited = gainers_df.head(max_stocks)
    
    st.info(f"Analyzing top {len(gainers_df_limited)} gainers... ~{len(gainers_df_limited) * 26} seconds")
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    filtered_data = []
    total = len(gainers_df_limited)
    
    for position, (idx, row) in enumerate(gainers_df_limited.iterrows()):
        symbol = row['Symbol']
        status_text.text(f"Checking {symbol}... ({position + 1}/{total})")
        
        # Get company overview for market cap
        overview = get_company_overview(symbol)
        time.sleep(13)
        
        if overview is None:
            progress_bar.progress((position + 1) / total)
            continue
        
        market_cap_millions = overview['market_cap_millions']
        
        # Filter: Market cap >= 30M
        if market_cap_millions < 30:
            progress_bar.progress((position + 1) / total)
            continue
        
        # Check for news
        news_count = check_news_sentiment(symbol, hours_back=24)
        time.sleep(13)
        
        # Only include if no news
        if news_count is not None and news_count > 0:
            progress_bar.progress((position + 1) / total)
            continue
        
        filtered_data.append({
            'Symbol': symbol,
            'Name': overview['name'],
            'Price': row['Price'],
            'Change %': row['Change %'],
            'Market Cap (M)': f"${market_cap_millions:.1f}M",
            'Volume': f"{int(row['Volume']):,}" if pd.notna(row['Volume']) else 'N/A'
        })
        
        progress_bar.progress((position + 1) / total)
    
    progress_bar.empty()
    status_text.empty()
    
    result = pd.DataFrame(filtered_data)
    return result

def fetch_earnings_calendar():
    """Fetch earnings calendar for next 3 months"""
    try:
        params = {
            'function': 'EARNINGS_CALENDAR',
            'horizon': '3month',
            'apikey': API_KEY
        }
        
        response = requests.get(BASE_URL, params=params, timeout=15)
        response.raise_for_status()
        
        try:
            json_data = response.json()
            if 'Error Message' in json_data:
                st.error(f"API Error: {json_data['Error Message']}")
                return pd.DataFrame()
            if 'Note' in json_data:
                st.warning(f"API Rate Limit: {json_data['Note']}")
                return pd.DataFrame()
            if 'Information' in json_data:
                st.warning(f"API Info: {json_data['Information']}")
                return pd.DataFrame()
        except:
            pass
        
        from io import StringIO
        df = pd.read_csv(StringIO(response.text))
        
        if df.empty:
            return pd.DataFrame()
        
        # Filter for tomorrow's earnings
        df['reportDate'] = pd.to_datetime(df['reportDate'], errors='coerce').dt.date
        tomorrow = (datetime.now() + timedelta(days=1)).date()
        
        df = df[df['reportDate'] == tomorrow]
        
        return df
        
    except Exception as e:
        st.error(f"Error fetching earnings: {e}")
        return pd.DataFrame()

def get_earnings_history(symbol):
    """Check if stock beat earnings 3+ times in last 4 quarters"""
    try:
        params = {
            'function': 'EARNINGS',
            'symbol': symbol,
            'apikey': API_KEY
        }
        
        response = requests.get(BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if 'Error Message' in data or 'Note' in data or 'Information' in data:
            return None
        
        if 'quarterlyEarnings' not in data:
            return None
        
        quarterly = data['quarterlyEarnings']
        
        if len(quarterly) < 4:
            return None
        
        beats = 0
        for i in range(4):
            reported = quarterly[i].get('reportedEPS')
            estimated = quarterly[i].get('estimatedEPS')
            
            if reported and estimated and reported != 'None' and estimated != 'None':
                try:
                    if float(reported) > float(estimated):
                        beats += 1
                except:
                    continue
        
        return beats >= 3
        
    except:
        return None

def filter_earnings_by_history(earnings_df, max_stocks=5):
    """Filter earnings by beat history"""
    if earnings_df.empty:
        return pd.DataFrame()
    
    earnings_df_limited = earnings_df.head(max_stocks)
    
    st.info(f"Checking earnings history for {len(earnings_df_limited)} stocks... ~{len(earnings_df_limited) * 13} seconds")
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    filtered_data = []
    total = len(earnings_df_limited)
    
    for position, (idx, row) in enumerate(earnings_df_limited.iterrows()):
        symbol = row['symbol']
        status_text.text(f"Checking {symbol}... ({position + 1}/{total})")
        
        beat_history = get_earnings_history(symbol)
        time.sleep(13)
        
        if beat_history:
            filtered_data.append({
                'Symbol': symbol,
                'Estimated EPS': row.get('estimate', 'N/A'),
                'Report Date': row.get('reportDate', 'N/A')
            })
        
        progress_bar.progress((position + 1) / total)
    
    progress_bar.empty()
    status_text.empty()
    
    return pd.DataFrame(filtered_data)

def main():
    st.set_page_config(page_title="Stock Analyzer", layout="wide")
    
    st.title("🚀 Aniket Mangalampalli's Stock Market Analyzer")
    st.markdown("---")
    
    if not API_KEY or API_KEY.strip() == "YOUR_API_KEY_HERE":
        st.error("⚠️ Please set your Alpha Vantage API key")
        st.info("Get FREE key: https://www.alphavantage.co/support/#api-key")
        st.stop()
    
    # Market status
    market_status = get_market_status()
    if market_status['is_open']:
        st.success(f"Market is OPEN | {market_status['current_time']}")
    else:
        st.info(f" Market is CLOSED | {market_status['current_time']}")
        st.caption("Note: TOP_GAINERS_LOSERS shows the most recent trading day data")
    
    st.warning("⏱Rate Limit: Free tier = 5 calls/min, 25/day. App waits 13s between calls.")
    
    # Section 1: Top Gainers
    st.header("Top Gainers Without News")
    st.caption("Price ≥ $3 | Gain ≥ 50% | Market Cap ≥ $30M | No Recent News (24hrs)")
    
    with st.spinner("Fetching top gainers from Alpha Vantage..."):
        gainers_df, last_updated = fetch_top_gainers()
    
    if last_updated:
        st.info(f"Data last updated: {last_updated}")

    if not gainers_df.empty:
        st.success(f"Found {len(gainers_df)} gainers meeting price/gain criteria")

        with st.expander("All Top Gainers (Before Filtering)", expanded=False):
            st.dataframe(gainers_df, use_container_width=True, hide_index=True)

        if st.button("Filter by Market Cap & News", type="primary"):
            filtered_gainers = filter_gainers_comprehensive(gainers_df, max_stocks=10)

            if not filtered_gainers.empty:
                st.success(f"{len(filtered_gainers)} stocks meet ALL criteria")
                st.dataframe(filtered_gainers, use_container_width=True, hide_index=True)
            else:
                st.warning("No stocks found meeting all criteria")
    else:
        st.warning("Unable to fetch gainers data. Check API status or rate limits.")
    
    st.markdown("---")
    
    # Section 2: Earnings
    st.header("Earnings Tomorrow - Predicted to Beat")
    st.caption("Beat estimates in 3+ of last 4 quarters")
    
    with st.spinner("Fetching earnings calendar..."):
        earnings_df = fetch_earnings_calendar()

    if not earnings_df.empty:
        st.success(f"Found {len(earnings_df)} stocks with earnings tomorrow")

        with st.expander("All Scheduled Earnings", expanded=False):
            st.dataframe(earnings_df.head(20), use_container_width=True, hide_index=True)

        if st.button("Filter by Beat History", type="primary"):
            filtered_earnings = filter_earnings_by_history(earnings_df, max_stocks=5)

            if not filtered_earnings.empty:
                st.success(f"{len(filtered_earnings)} stocks with strong beat history")
                st.dataframe(filtered_earnings, use_container_width=True, hide_index=True)
            else:
                st.warning("No stocks found with 3+ beats in last 4 quarters")
    else:
        st.warning("No earnings scheduled for tomorrow or unable to fetch data")
    
    st.markdown("---")
    st.caption(f"Data: Alpha Vantage API | Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    st.caption("Developed by Aniket Mangalampalli")
    st.caption("ℹTOP_GAINERS_LOSERS endpoint provides real-time data during market hours and most recent trading day data when market is closed")

if __name__ == "__main__":
    main()