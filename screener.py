import pandas as pd
import yfinance as yf
from ta.trend import EMAIndicator

def analyze_index(ticker):
    df = yf.download(ticker, period="6mo", interval="1d", progress=False)

    if df.empty:
        return {"Close": "n/a", "EMA10": "n/a", "EMA20": "n/a", "EMA200": "n/a"}

    if 'Close' not in df.columns:
        if 'Adj Close' in df.columns:
            df['Close'] = df['Adj Close']
        else:
            return {"Close": "n/a", "EMA10": "n/a", "EMA20": "n/a", "EMA200": "n/a"}

    # Fallback falls keine gültigen Close-Werte da sind
    null_count = df['Close'].isnull().sum()
    total_rows = len(df)

    # Sicherstellen, dass null_count ein int ist!
    if int(null_count) >= int(total_rows):
        return {"Close": "n/a", "EMA10": "n/a", "EMA20": "n/a", "EMA200": "n/a"}

    df['EMA10'] = EMAIndicator(close=df['Close'], window=10).ema_indicator()
    df['EMA20'] = EMAIndicator(close=df['Close'], window=20).ema_indicator()
    df['EMA200'] = EMAIndicator(close=df['Close'], window=200).ema_indicator()

    latest = df.iloc[-1]

    return {
        "Close": round(latest['Close'], 2),
        "EMA10": round(latest['EMA10'], 2),
        "EMA20": round(latest['EMA20'], 2),
        "EMA200": round(latest['EMA200'], 2)
    }

def get_index_status():
    return {
        "SPY": analyze_index("SPY"),
        "QQQ": analyze_index("QQQ")
    }

def run_screening():
    data = {
        "Ticker": ["AAPL", "MSFT"],
        "Signal": ["Breakout", "Reversal"],
        "Take Profit": ["+5%", "+3%"]
    }
    return pd.DataFrame(data)
