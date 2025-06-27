import pandas as pd
import yfinance as yf

def get_index_status():
    indexes = ["SPY", "QQQ"]
    status = {}
    for ticker in indexes:
        result = analyze_index(ticker)
        status[ticker] = result
    return status

def analyze_index(ticker):
    df = yf.download(ticker, period="6mo", interval="1d", progress=False)
    if df.empty or 'Close' not in df.columns:
        return {
            "Close": "n/a",
            "EMA10": "n/a", "EMA10_value": "n/a",
            "EMA20": "n/a", "EMA20_value": "n/a",
            "EMA200": "n/a", "EMA200_value": "n/a"
        }

    df.dropna(subset=['Close'], inplace=True)

    # Berechne EMAs robust per pandas ewm
    df['EMA10'] = df['Close'].ewm(span=10, adjust=False).mean()
    df['EMA20'] = df['Close'].ewm(span=20, adjust=False).mean()
    df['EMA200'] = df['Close'].ewm(span=200, adjust=False).mean()

    latest = df.iloc[-1]

    close = latest['Close']
    ema10 = latest['EMA10']
    ema20 = latest['EMA20']
    ema200 = latest['EMA200']

    return {
        "Close": round(close, 2),
        "EMA10": "über" if close > ema10 else "unter",
        "EMA10_value": round(ema10, 2),
        "EMA20": "über" if close > ema20 else "unter",
        "EMA20_value": round(ema20, 2),
        "EMA200": "über" if close > ema200 else "unter",
        "EMA200_value": round(ema200, 2)
    }

def run_screening():
    # Dummy-Treffer, damit du siehst, dass es funktioniert
    data = {
        "Ticker": ["AAPL", "MSFT"],
        "Signal": ["Breakout", "EMA Reclaim"],
        "Einstieg": ["Intraday", "Daily"],
        "CRV": [2.5, 1.8]
    }
    df = pd.DataFrame(data)
    return df
