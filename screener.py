import pandas as pd
import yfinance as yf

def get_index_status():
    indexes = ["SPY", "QQQ"]
    status = {}
    for ticker in indexes:
        status[ticker] = analyze_index(ticker)
    return status

def analyze_index(ticker):
    df = yf.download(ticker, period="6mo", interval="1d", progress=False)

    # Fallback: Falls nur Adj Close da ist → nutze diese
    if 'Close' not in df.columns and 'Adj Close' in df.columns:
        df['Close'] = df['Adj Close']

    # Wenn immer noch keine Spalte 'Close' → gib sauber zurück
    if 'Close' not in df.columns:
        return {
            "Close": "n/a",
            "EMA10": "n/a", "EMA10_value": "n/a",
            "EMA20": "n/a", "EMA20_value": "n/a",
            "EMA200": "n/a", "EMA200_value": "n/a"
        }

    df = df.dropna(subset=['Close'])
    if df.empty:
        return {
            "Close": "n/a",
            "EMA10": "n/a", "EMA10_value": "n/a",
            "EMA20": "n/a", "EMA20_value": "n/a",
            "EMA200": "n/a", "EMA200_value": "n/a"
        }

    df['EMA10'] = df['Close'].ewm(span=10).mean()
    df['EMA20'] = df['Close'].ewm(span=20).mean()
    df['EMA200'] = df['Close'].ewm(span=200).mean()

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
    # DUMMY: Funktioniert, ohne echten Check
    data = {
        "Ticker": ["AAPL", "MSFT"],
        "Signal": ["Breakout", "EMA Reclaim"],
        "Einstieg": ["Intraday", "Daily"],
        "CRV": [2.5, 1.8]
    }
    df = pd.DataFrame(data)
    return df
