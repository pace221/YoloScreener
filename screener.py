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
        print(f"[Fehler Tickers]: {e}")
        return []

def calculate_ema(series, window):
    return series.ewm(span=window, adjust=False).mean()

def analyze_index(ticker):
    df = yf.download(ticker, period="6mo", interval="1d", progress=False)
    if df.empty or 'Close' not in df.columns:
        return {
            "Close": "n/a",
            "EMA10": {"Status": "n/a", "Wert": "n/a"},
            "EMA20": {"Status": "n/a", "Wert": "n/a"},
            "EMA200": {"Status": "n/a", "Wert": "n/a"}
        }

    df.dropna(subset=['Close'], inplace=True)
    df['EMA10'] = calculate_ema(df['Close'], 10)
    df['EMA20'] = calculate_ema(df['Close'], 20)
    df['EMA200'] = calculate_ema(df['Close'], 200)

    # Nur Zeilen mit vollständigen EMA-Werten
    df = df.dropna(subset=['EMA10', 'EMA20', 'EMA200'])
    if df.empty:
        return {
            "Close": "n/a",
            "EMA10": {"Status": "n/a", "Wert": "n/a"},
            "EMA20": {"Status": "n/a", "Wert": "n/a"},
            "EMA200": {"Status": "n/a", "Wert": "n/a"}
        }

    latest = df.iloc[-1]
    close = latest['Close']
    ema10 = latest['EMA10']
    ema20 = latest['EMA20']
    ema200 = latest['EMA200']

    return {
        "Close": round(close, 2),
        "EMA10": {
            "Status": "über" if close > ema10 else "unter",
            "Wert": round(ema10, 2)
        },
        "EMA20": {
            "Status": "über" if close > ema20 else "unter",
            "Wert": round(ema20, 2)
        },
        "EMA200": {
            "Status": "über" if close > ema200 else "unter",
            "Wert": round(ema200, 2)
        }
    }

def get_index_status():
    return {
        "SPY": analyze_index("SPY"),
        "QQQ": analyze_index("QQQ")
    }

# Alle weiteren Funktionen unverändert:
# analyze_stock, save_results, load_recent_stats, get_company_name, generate_ko_link
# (Die aus der letzten Version bitte lassen!)
