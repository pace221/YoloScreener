import pandas as pd
import yfinance as yf
from ta.trend import EMAIndicator
import datetime

def get_tickers():
    tables = pd.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")
    sp500 = tables[0]['Symbol'].tolist()
    return sp500[:10]  # Teste mit kleinerer Liste

def calculate_ema(series, window):
    return EMAIndicator(close=series, window=window).ema_indicator()

def analyze_index(ticker):
    df = yf.download(ticker, period="3mo", interval="1d", progress=False)

    if df.empty:
        return {"Close": "n/a", "EMA10": "n/a", "EMA20": "n/a", "EMA200": "n/a"}

    if 'Close' not in df.columns:
        if 'Adj Close' in df.columns:
            df['Close'] = df['Adj Close']
        else:
            return {"Close": "n/a", "EMA10": "n/a", "EMA20": "n/a", "EMA200": "n/a"}

    if df['Close'].isnull().all():
        return {"Close": "n/a", "EMA10": "n/a", "EMA20": "n/a", "EMA200": "n/a"}

    df = df.dropna(subset=['Close'])
    if df.empty:
        return {"Close": "n/a", "EMA10": "n/a", "EMA20": "n/a", "EMA200": "n/a"}

    df['EMA10'] = calculate_ema(df['Close'], 10)
    df['EMA20'] = calculate_ema(df['Close'], 20)
    df['EMA200'] = calculate_ema(df['Close'], 200)

    latest = df.iloc[-1]

    close_price = float(latest['Close'])
    ema10 = float(latest['EMA10'])
    ema20 = float(latest['EMA20'])
    ema200 = float(latest['EMA200'])

    return {
        "Close": f"{close_price:.2f}",
        "EMA10": f"{'über' if close_price > ema10 else 'unter'} ({ema10:.2f})",
        "EMA20": f"{'über' if close_price > ema20 else 'unter'} ({ema20:.2f})",
        "EMA200": f"{'über' if close_price > ema200 else 'unter'} ({ema200:.2f})"
    }

def get_index_status():
    return {
        "SPY": analyze_index("SPY"),
        "QQQ": analyze_index("QQQ")
    }

def analyze_stock(ticker, selected_signals):
    df = yf.download(ticker, period="6mo", interval="1d", progress=False)
    if df.empty:
        return None

    if 'Close' not in df.columns:
        if 'Adj Close' in df.columns:
            df['Close'] = df['Adj Close']
        else:
            return None

    if df['Close'].isnull().all():
        return None

    df = df.dropna(subset=['Close'])
    if len(df) < 30:
        return None

    latest = df.iloc[-1]
    triggered = []

    if "EMA Crossover" in selected_signals:
        df['EMA10'] = calculate_ema(df['Close'], 10)
        df['EMA20'] = calculate_ema(df['Close'], 20)
        if latest['EMA10'] > latest['EMA20']:
            triggered.append("EMA Crossover")

    if "Breakout" in selected_signals:
        breakout = df['High'].rolling(window=20).max().iloc[-2]
        if latest['Close'] > breakout:
            triggered.append("Breakout")

    if not triggered:
        return None

    return {
        "Ticker": ticker,
        "Date": datetime.datetime.now().strftime("%Y-%m-%d"),
        "Signals": ", ".join(triggered),
        "Close": round(latest['Close'], 2)
    }
