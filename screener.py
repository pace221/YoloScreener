import yfinance as yf
import pandas as pd
from ta.trend import EMAIndicator
from ta.momentum import RSIIndicator
from datetime import datetime

def get_tickers():
    # Kombiniere S&P500 + NASDAQ100 aus Wikipedia
    sp500 = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]['Symbol'].tolist()
    nasdaq = pd.read_html('https://en.wikipedia.org/wiki/NASDAQ-100')[4]['Ticker'].tolist()
    tickers = list(set(sp500 + nasdaq))
    return tickers

def analyze_stock(ticker, active_signals):
    try:
        df = yf.download(ticker, period="6mo", interval="1d", progress=False)
        if df.empty or 'Close' not in df:
            return None
        df.dropna(inplace=True)
    except:
        return None

    df['EMA10'] = EMAIndicator(df['Close'], window=10).ema_indicator()
    df['EMA20'] = EMAIndicator(df['Close'], window=20).ema_indicator()
    df['EMA200'] = EMAIndicator(df['Close'], window=200).ema_indicator()
    df['RSI'] = RSIIndicator(df['Close'], window=14).rsi()

    latest = df.iloc[-1]
    signals_detected = []

    # Beispielhafte Logik für jedes Signal
    if "EMA Reclaim" in active_signals:
        if df['Close'].iloc[-2] < df['EMA20'].iloc[-2] and latest['Close'] > latest['EMA20']:
            signals_detected.append("EMA Reclaim")

    if "Breakout 20d High" in active_signals:
        if latest['Close'] > df['High'].rolling(window=20).max().iloc[-2]:
            signals_detected.append("Breakout 20d High")

    if "RSI > 60" in active_signals:
        if latest['RSI'] > 60:
            signals_detected.append("RSI > 60")

    if "Volumen-Breakout" in active_signals:
        vol_avg = df['Volume'].rolling(window=20).mean().iloc[-1]
        if latest['Volume'] > vol_avg:
            signals_detected.append("Volumen-Breakout")

    if "Inside Day" in active_signals:
        if df['High'].iloc[-1] < df['High'].iloc[-2] and df['Low'].iloc[-1] > df['Low'].iloc[-2]:
            signals_detected.append("Inside Day")

    if "Cup-with-Handle" in active_signals:
        # Platzhalter: Erkennung nicht trivial – hier nur Dummy
        if latest['Close'] > latest['EMA200']:
            signals_detected.append("Cup-with-Handle")

    if "SFP" in active_signals:
        if df['Low'].iloc[-1] < df['Low'].iloc[-2] and latest['Close'] > df['Close'].iloc[-2]:
            signals_detected.append("SFP")

    if not signals_detected:
        return None

    # Entry, SL, TP (Platzhalter)
    entry = round(latest['Close'], 2)
    stop = round(entry * 0.97, 2)
    tp1 = round(entry * 1.05, 2)
    tp2 = round(entry * 1.10, 2)
    crv = round((tp1 - entry) / (entry - stop), 2)

    return {
        "Ticker": ticker,
        "Name": get_company_name(ticker),
        "Signals Detected": ", ".join(signals_detected),
        "Entry ($)": entry,
        "TP1 ($)": tp1,
        "TP2 ($)": tp2,
        "SL ($)": stop,
        "CRV": crv,
        "KO-Link": generate_ko_link(ticker)
    }

def get_company_name(ticker):
    try:
        info = yf.Ticker(ticker).info
        return info.get("shortName", "n/a")
    except:
        return "n/a"

def generate_ko_link(ticker):
    return f"https://www.onvista.de/derivate/suche?SEARCH_VALUE={ticker}&TYPE=Knockouts"

def calculate_ema(series, window):
    return EMAIndicator(close=series, window=window).ema_indicator()

def get_index_status():
    return {
        "SPY": analyze_index("SPY"),
        "QQQ": analyze_index("QQQ")
    }

def analyze_index(ticker):
    df = yf.download(ticker, period="3mo", interval="1d", progress=False)
    if df.empty:
        return {"EMA10": "n/a", "EMA20": "n/a", "EMA200": "n/a"}

    df['EMA10'] = calculate_ema(df['Close'], 10)
    df['EMA20'] = calculate_ema(df['Close'], 20)
    df['EMA200'] = calculate_ema(df['Close'], 200)
    latest = df.iloc[-1]

    try:
        return {
            "EMA10": "über" if latest['Close'] > latest['EMA10'] else "unter",
            "EMA20": "über" if latest['Close'] > latest['EMA20'] else "unter",
            "EMA200": "über" if latest['Close'] > latest['EMA200'] else "unter"
        }
    except:
        return {"EMA10": "n/a", "EMA20": "n/a", "EMA200": "n/a"}
