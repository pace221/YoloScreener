import yfinance as yf
import pandas as pd
from datetime import datetime

RISK_EUR = 100
EURUSD = 1.08
RISK_USD = RISK_EUR * EURUSD

def get_tickers():
    sp500 = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]['Symbol'].tolist()
    nasdaq = pd.read_html('https://en.wikipedia.org/wiki/NASDAQ-100')[4]['Ticker'].tolist()
    tickers = list(set(sp500 + nasdaq))
    return [t.replace('.', '-') for t in tickers]

def calculate_ema(series, window):
    return series.ewm(span=window, adjust=False).mean()

def calculate_rsi(series, window=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=window).mean()
    avg_loss = loss.rolling(window=window).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def analyze_index(ticker):
    df = yf.download(ticker, period="3mo", interval="1d", progress=False)
    if df.empty:
        return {"EMA10": "n/a", "EMA20": "n/a", "EMA200": "n/a"}

    df['EMA10'] = calculate_ema(df['Close'], 10)
    df['EMA20'] = calculate_ema(df['Close'], 20)
    df['EMA200'] = calculate_ema(df['Close'], 200)
    latest = df.iloc[-1]

    return {
        "EMA10": "über" if latest['Close'] > latest['EMA10'] else "unter",
        "EMA20": "über" if latest['Close'] > latest['EMA20'] else "unter",
        "EMA200": "über" if latest['Close'] > latest['EMA200'] else "unter"
    }

def analyze_stock(ticker):
    try:
        df = yf.download(ticker, period="3mo", interval="1d", progress=False)
        df.dropna(inplace=True)
        if df.shape[0] < 25:
            return None

        df['EMA10'] = calculate_ema(df['Close'], 10)
        df['EMA20'] = calculate_ema(df['Close'], 20)
        df['EMA200'] = calculate_ema(df['Close'], 200)
        df['Volume_MA20'] = df['Volume'].rolling(window=20).mean()
        df['RSI'] = calculate_rsi(df['Close'])

        latest = df.iloc[-1]
        prev = df.iloc[-2]
        signals = []

        if prev['Close'] < prev['EMA10'] and latest['Close'] > latest['EMA10']:
            signals.append("EMA10 Reclaim")
        if prev['Close'] < prev['EMA20'] and latest['Close'] > latest['EMA20']:
            signals.append("EMA20 Reclaim")
        if latest['Close'] > df['Close'][-20:].max():
            signals.append("Breakout 20d High")
        if latest['Low'] < df['Low'][-5:-1].min() and latest['Close'] > df['Low'][-5:-1].min():
            signals.append("SFP Rebound")
        window = df['Close'][-20:]
        if window.min() < window.mean() * 0.95 and latest['Close'] > window.max():
            signals.append("Cup w/ Handle")
        if df['High'].iloc[-2] > latest['High'] and df['Low'].iloc[-2] < latest['Low']:
            signals.append("Inside Day Breakout")
        if latest['RSI'] > 60:
            signals.append("RSI > 60")
        if latest['Volume'] > latest['Volume_MA20']:
            signals.append("Volumen-Breakout")

        if not signals:
            return None

        info = yf.Ticker(ticker).info
        name = info.get("shortName", "n/a")

        entry = round(latest['Close'] * 1.0025, 2)
        stop = round(min(latest['Low'], latest['EMA20']), 2)
        risk_per_share = entry - stop
        if risk_per_share <= 0:
            return None

        qty = int(RISK_USD / risk_per_share)
        tp1 = round(entry + 1 * risk_per_share, 2)
        tp2 = round(entry + 2 * risk_per_share, 2)
        tp3 = round(entry + 3 * risk_per_share, 2)
        crv = round((tp1 - entry) / (entry - stop), 2)

        ko_schwelle = round(stop - (0.01 * stop), 2)
        ko_abstand = round(((entry - ko_schwelle) / ko_schwelle) * 100, 2)
        ko_link = f"https://www.onvista.de/derivate/suche/?searchValue={ticker}+long"

        return {
            "Ticker": ticker,
            "Name": name,
            "Entry (USD)": entry,
            "Stop (USD)": stop,
            "Risk/Share": round(risk_per_share, 2),
            "Qty (1R=100€)": qty,
            "TP1": tp1,
            "TP2": tp2,
            "TP3": tp3,
            "CRV": crv,
            "Signals Detected": ", ".join(signals),
            "KO-Richtung": "Long",
            "KO-Schwelle": ko_schwelle,
            "Abstand KO %": ko_abstand,
            "KO-Link": ko_link,
            "Empfehlung": "Intraday Entry auf H1"
        }

    except Exception:
        return None

def run_screening():
    tickers = get_tickers()
    results = []
    for ticker in tickers:
        res = analyze_stock(ticker)
        if res:
            results.append(res)
    return pd.DataFrame(results)

def get_index_status():
    spy_status = analyze_index("SPY")
    qqq_status = analyze_index("QQQ")
    return {"SPY": spy_status, "QQQ": qqq_status}
