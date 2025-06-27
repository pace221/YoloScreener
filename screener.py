import pandas as pd
import yfinance as yf

def calculate_ema(series, window):
    return series.ewm(span=window, adjust=False).mean()

def analyze_index(ticker):
    df = yf.download(ticker, period="6mo", interval="1d", progress=False)

    if df.empty:
        return {"Close": "n/a", "EMA10": "n/a", "EMA20": "n/a", "EMA200": "n/a"}

    if 'Close' not in df.columns:
        if 'Adj Close' in df.columns:
            df['Close'] = df['Adj Close']
        else:
            return {"Close": "n/a", "EMA10": "n/a", "EMA20": "n/a", "EMA200": "n/a"}

    null_count = int(df['Close'].isnull().sum())
    total_rows = len(df)

    if null_count >= total_rows:
        return {"Close": "n/a", "EMA10": "n/a", "EMA20": "n/a", "EMA200": "n/a"}

    df['EMA10'] = calculate_ema(df['Close'], 10)
    df['EMA20'] = calculate_ema(df['Close'], 20)
    df['EMA200'] = calculate_ema(df['Close'], 200)

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
