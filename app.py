import streamlit as st
import pandas as pd
import sys
import os

sys.path.append(os.path.dirname(__file__))

from screener import (
    get_tickers,
    analyze_stock,
    get_index_status,
    update_signal_history
)

st.title("📈 YOLO Screener")

# Marktstatus
st.header("📊 Marktstatus")
index_status = get_index_status()

for index, status in index_status.items():
    st.subheader(f"{index} Status")
    st.write(f"EMA10: {status['EMA10']} | EMA20: {status['EMA20']} | EMA200: {status['EMA200']}")
    st.write(f"Close: {status['Close']:.2f}")

# Screening starten
st.header("🔍 Screening")

signals = [
    "EMA Crossover",
    "Breakout",
    "Trend Continuation"
]

selected_signals = st.multiselect(
    "Welche Signale willst du prüfen?",
    options=signals,
    default=signals
)

run_button = st.button("📡 Screening starten")

if run_button:
    tickers = get_tickers()
    results = []
    progress = st.progress(0)
    for i, ticker in enumerate(tickers):
        res = analyze_stock(ticker, selected_signals)
        if res:
            results.append(res)
        progress.progress((i + 1) / len(tickers))

    if results:
        df = pd.DataFrame(results)
        st.dataframe(df)
    else:
        st.info("Kein Treffer gefunden.")
