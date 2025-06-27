import pandas as pd
import yfinance as yf
from ta.trend import EMAIndicator
import datetime

# Hole SP500 Ticker (Test: nur 10!)
def get_tickers():
    tables = pd.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")
    sp500 = tables[0]['Symbol'].tolist()
    return sp500[:10]  # Für Tests

# EMA Berechnung
def calculate_ema(series, window):
    return EMAIndicator(close=series, window=window).ema_indicator()

# Index-Analyse robust
def analyze_index(ticker):
    df = yf.download(ticker, period="3mo", interval="1d", progress=False)

    if df.empty or 'Close' not in df.columns:
        return {"Close": "n/a", "EMA10": "n/a", "EMA20": "n/a", "EMA200": "n/a"}

    df.dropna(subset=['Close'], inplace=True)
    if df.empty:
        return {"Close": "n/a", "EMA10": "n/a", "EMA20": "n/a", "EMA200": "n/a"}

    df['EMA10'] = calculate_ema(df['Close'], 10)
    df['EMA20'] = calculate_ema(df['Close'], 20)
    df['EMA200'] = calculate_ema(df['Close'], 200)

    latest = df.iloc[-1]

    return {
        "Close": round(latest['Close'], 2),
        "EMA10": f"{'über' if latest['Close'] > latest['EMA10'] else 'unter'} ({round(latest['EMA10'], 2)})",
        "EMA20": f"{'über' if latest['Close'] > latest['EMA20'] else 'unter'} ({round(latest['EMA20'], 2)})",
        "EMA200": f"{'über' if latest['Close'] > latest['EMA200'] else 'unter'} ({round(latest['EMA200'], 2)})",
    }

# Gesamtstatus
def get_index_status():
    return {
        "SPY": analyze_index("SPY"),
        "QQQ": analyze_index("QQQ")
    }

# Signal-Check pro Aktie
def analyze_stock(ticker, selected_signals):
    df = yf.download(ticker, period="6mo", interval="1d", progress=False)
    if df.empty or 'Close' not in df.columns:
        return None

    df.dropna(subset=['Close'], inplace=True)
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
