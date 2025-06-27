import pandas as pd
import yfinance as yf

def get_tickers():
    """Lade S&P500 Ticker"""
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    df = pd.read_html(url)[0]
    return df['Symbol'].tolist()

def analyze_stock(ticker):
    """Einfaches Screening: Close > EMA10"""
    df = yf.download(ticker, period="6mo", interval="1d", progress=False)

    # Fallback: nutze Adj Close, falls Close fehlt
    if 'Close' not in df.columns:
        if 'Adj Close' in df.columns:
            df['Close'] = df['Adj Close']

    # Prüfe erneut, ob Close jetzt da ist
    if 'Close' not in df.columns:
        return None  # Ticker überspringen

    # Prüfe ob Spalte mindestens 1 Wert hat
    if df['Close'].dropna().empty:
        return None

    # Berechne EMA10
    df['EMA10'] = df['Close'].ewm(span=10).mean()

    # Prüfe Bedingung
    latest = df.dropna(subset=['Close']).iloc[-1]

    if latest['Close'] > latest['EMA10']:
        return {
            "Ticker": ticker,
            "Close": round(latest['Close'], 2),
            "EMA10": round(latest['EMA10'], 2),
            "Signal": "Close > EMA10"
        }
    return None

def run_screening():
    tickers = get_tickers()
    results = []

    for ticker in tickers:
        res = analyze_stock(ticker)
        if res:
            results.append(res)

    if results:
        return pd.DataFrame(results)
    else:
        return pd.DataFrame(columns=["Ticker", "Close", "EMA10", "Signal"])
