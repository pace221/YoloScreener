import pandas as pd
import yfinance as yf
from ta.trend import EMAIndicator
import datetime

# =============== Ticker Liste ===============
def get_tickers():
    # Hole SP500 Ticker von Wikipedia
    tables = pd.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")
    sp500 = tables[0]['Symbol'].tolist()

    # Beispiel: Du kannst hier noch NASDAQ Ticker hinzufügen, wenn du willst
    # nasdaq = ["AAPL", "MSFT", ...]
    return sp500


# =============== EMA Berechnung ===============
def calculate_ema(series, window):
    return EMAIndicator(close=series, window=window).ema_indicator()


# =============== Index Analyse ===============
def analyze_index(ticker):
    df = yf.download(ticker, period="3mo", interval="1d", progress=False)

    if df.empty:
        return {"EMA10": "n/a", "EMA20": "n/a", "EMA200": "n/a", "Close": "n/a"}

    if 'Close' not in df.columns:
        return {"EMA10": "n/a", "EMA20": "n/a", "EMA200": "n/a", "Close": "n/a"}

    df.dropna(subset=['Close'], inplace=True)

    if df.empty:
        return {"EMA10": "n/a", "EMA20": "n/a", "EMA200": "n/a", "Close": "n/a"}

    df['EMA10'] = calculate_ema(df['Close'], 10)
    df['EMA20'] = calculate_ema(df['Close'], 20)
    df['EMA200'] = calculate_ema(df['Close'], 200)

    latest = df.iloc[-1]

    return {
        "EMA10": "über" if latest['Close'] > latest['EMA10'] else "unter",
        "EMA20": "über" if latest['Close'] > latest['EMA20'] else "unter",
        "EMA200": "über" if latest['Close'] > latest['EMA200'] else "unter",
        "Close": round(latest['Close'], 2)
    }


def get_index_status():
    return {
        "SPY": analyze_index("SPY"),
        "QQQ": analyze_index("QQQ")
    }


# =============== Signal Analyse pro Aktie ===============
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
        breakout_level = df['High'].rolling(window=20).max().iloc[-2]
        if latest['Close'] > breakout_level:
            triggered.append("Breakout")

    if "Trend Continuation" in selected_signals:
        ema20 = calculate_ema(df['Close'], 20).iloc[-1]
        if latest['Close'] > ema20 and latest['Close'] > df['Close'].iloc[-2]:
            triggered.append("Trend Continuation")

    if not triggered:
        return None

    return {
        "Ticker": ticker,
        "Date": datetime.datetime.now().strftime("%Y-%m-%d"),
        "Triggered Signals": ", ".join(triggered),
        "Last Close": round(latest['Close'], 2)
    }
