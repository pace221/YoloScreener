import pandas as pd
import yfinance as yf

def get_tickers():
    """Lade S&P500 Ticker"""
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    df = pd.read_html(url)[0]
    return df['Symbol'].tolist()

def analyze_stock(ticker):
    """Prüft Beispiel: Close > EMA10"""
    df = yf.download(ticker, period="6mo", interval="1d", progress=False)

    # Fallback: nutze Adj Close wenn Close fehlt
    if 'Close' not in df.columns:
        if 'Adj Close' in df.columns:
            df['Close'] = df['Adj Close']
        else:
            return None  # Keiner vorhanden

    # Wenn Close-Spalte jetzt fehlt: abbrechen
    if 'Close' not in df.columns:
        return None

    df = df.dropna(subset=['Close'])
    if df.empty or len(df) < 10:
        return None

    df['EMA10'] = df['Close'].ewm(span=10).mean()

    latest = df.iloc[-1]
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
