import streamlit as st
import pandas as pd
import screener

st.set_page_config(page_title="📈 YOLO Screener")

st.title("📈 YOLO Screener")
st.subheader("📊 Marktstatus")

index_status = screener.get_index_status()
for index, status in index_status.items():
    st.write(f"**{index}** - Close: {status['Close']}")
    st.write(f"EMA10: {status['EMA10']}, EMA20: {status['EMA20']}, EMA200: {status['EMA200']}")

st.divider()

st.subheader("Signale auswählen")
available_signals = ["EMA Crossover", "Breakout"]
selected_signals = st.multiselect("Welche Signale möchtest du prüfen?", available_signals)

if st.button("🔍 Screening starten"):
    if not selected_signals:
        st.warning("Bitte wähle mindestens ein Signal.")
    else:
        tickers = screener.get_tickers()
        total = len(tickers)
        progress = st.progress(0)
        results = []

        for i, ticker in enumerate(tickers):
            res = screener.analyze_stock(ticker, selected_signals)
            if res:
                results.append(res)
            progress.progress((i + 1) / total)

        if results:
            df = pd.DataFrame(results)
            st.success(f"{len(results)} Treffer gefunden!")
            st.dataframe(df)
        else:
            st.info("Keine Treffer für die aktuellen Kriterien.")
