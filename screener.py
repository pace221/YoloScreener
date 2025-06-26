import yfinance as yf
import pandas as pd
from datetime import date
import os

HISTORY_FILE = "results.csv"

def get_tickers():
    try:
        sp500 = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]['Symbol'].tolist()
        nasdaq = pd.read_html('https://en.wikipedia.org/wiki/NASDAQ-100')[4]['Ticker'].tolist()
        return list(set(sp500 + nasdaq))
    except Exception as e:
        print(f"[Fehler] Ticker-Import: {e}")
        return []

def calculate_ema(series, window):
    return series.ewm(span=window, adjust=False).mean()

def calculate_rsi(series, window=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0).rolling(window=window).mean()
    loss = -delta.where(delta < 0, 0).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def analyze_index(ticker):
    try:
        df = yf.download(ticker, period="12mo", interval="1d", progress=False)
        if df.empty or 'Close' not in df.columns:
            raise ValueError(f"{ticker} enthält keine gültige 'Close'-Spalte.")

        df = df.dropna(subset=['Close']).copy()
        if len(df) < 220:
            raise ValueError(f"{ticker}: Nicht genügend Daten für EMA200 (mind. 220 Tage).")

        df['EMA10'] = calculate_ema(df['Close'], 10)
        df['EMA20'] = calculate_ema(df['Close'], 20)
        df['EMA200'] = calculate_ema(df['Close'], 200)

        latest = df.iloc[-1]
        ema10 = latest.get('EMA10')
        ema20 = latest.get('EMA20')
        ema200 = latest.get('EMA200')
        close = latest.get('Close')

        return {
            "EMA10": "über" if close > ema10 else "unter",
            "EMA20": "über" if close > ema20 else "unter",
            "EMA200": "über" if close > ema200 else "unter"
        }

    except Exception as e:
        print(f"[Fehler analyze_index] {ticker}: {e}")
        return {"EMA10": "n/a", "EMA20": "n/a", "EMA200": "n/a"}

def get_index_status():
    return {
        "SPY": analyze_index("SPY"),
        "QQQ": analyze_index("QQQ")
    }

def analyze_stock(ticker, active_signals):
    try:
        df = yf.download(ticker, period="6mo", interval="1d", progress=False)
        if df.empty or 'Close' not in df.columns:
            return None
        df.dropna(inplace=True)
        df['EMA10'] = calculate_ema(df['Close'], 10)
        df['EMA20'] = calculate_ema(df['Close'], 20)
        df['EMA200'] = calculate_ema(df['Close'], 200)
        df['RSI'] = calculate_rsi(df['Close'])

        latest = df.iloc[-1]
        signals_detected = []

        if "EMA Reclaim" in active_signals:
            if df['Close'].iloc[-2] < df['EMA20'].iloc[-2] and latest['Close'] > latest['EMA20']:
                signals_detected.append("EMA Reclaim")
        if "Breakout 20d High" in active_signals:
            highest_20d = df['High'].rolling(window=20).max().shift(1)
            if latest['Close'] > highest_20d.iloc[-1]:
                signals_detected.append("Breakout 20d High")
        if "RSI > 60" in active_signals and latest['RSI'] > 60:
            signals_detected.append("RSI > 60")
        if "Volumen-Breakout" in active_signals:
            vol_avg = df['Volume'].rolling(window=20).mean().iloc[-1]
            if latest['Volume'] > vol_avg:
                signals_detected.append("Volumen-Breakout")
        if "Inside Day" in active_signals:
            if df['High'].iloc[-1] < df['High'].iloc[-2] and df['Low'].iloc[-1] > df['Low'].iloc[-2]:
                signals_detected.append("Inside Day")
        if "Cup-with-Handle" in active_signals and latest['Close'] > latest['EMA200']:
            signals_detected.append("Cup-with-Handle")
        if "SFP" in active_signals:
            if df['Low'].iloc[-1] < df['Low'].iloc[-2] and latest['Close'] > df['Close'].iloc[-2]:
                signals_detected.append("SFP")

        if not signals_detected:
            return None

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
    except Exception as e:
        print(f"[Fehler Analyse {ticker}]: {e}")
        return None

def get_company_name(ticker):
    try:
        info = yf.Ticker(ticker).info
        return info.get("shortName", "n/a")
    except:
        return "n/a"

def generate_ko_link(ticker):
    return f"https://www.onvista.de/derivate/suche?SEARCH_VALUE={ticker}&TYPE=Knockouts"

def save_results(results_df):
    if results_df.empty:
        return
    today = date.today().isoformat()
    results_df = results_df.copy()
    results_df["Datum"] = today
    if os.path.exists(HISTORY_FILE):
        old = pd.read_csv(HISTORY_FILE)
        combined = pd.concat([old, results_df], ignore_index=True)
    else:
        combined = results_df
    combined.to_csv(HISTORY_FILE, index=False)

def load_recent_stats(days=30):
    if not os.path.exists(HISTORY_FILE):
        return pd.DataFrame()
    df = pd.read_csv(HISTORY_FILE)
    df["Datum"] = pd.to_datetime(df["Datum"])
    cutoff = pd.Timestamp.today() - pd.Timedelta(days=days)
    return df[df["Datum"] >= cutoff]
