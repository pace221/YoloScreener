import streamlit as st
from screener import (
    get_tickers,
    analyze_stock,
    get_index_status,
    save_results,
    load_recent_stats,
)
import pandas as pd

st.set_page_config(page_title="YOLO Screener", layout="wide")
st.title("📈 YOLO Aktien Screener")

# Marktstatus
st.subheader("📊 Marktstatus")
index_status = get_index_status()
for index, status in index_status.items():
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"**{index}**")
    with col2:
        st.markdown(f"EMA10: `{status['EMA10']}`")
    with col3:
        st.markdown(f"EMA20: `{status['EMA20']}`")
    with col4:
        st.markdown(f"EMA200: `{status['EMA200']}`")

# Auswahl der Signale
st.subheader("🔍 Signal-Auswahl")
all_signals = [
    "EMA Reclaim",
    "Breakout 20d High",
    "RSI > 60",
    "Volumen-Breakout",
    "Inside Day",
    "Cup-with-Handle",
    "SFP"
]

col_master, *_ = st.columns(4)
select_all = col_master.checkbox("Alle auswählen", value=False)

if select_all:
    selected_signals = st.multiselect("Welche Signale sollen gescreent werden?", all_signals, default=all_signals)
else:
    selected_signals = st.multiselect("Welche Signale sollen gescreent werden?", all_signals)

# Screening starten
if st.button("🚀 Screening starten"):
    tickers = get_tickers()
    results = []
    progress = st.progress(0)
    status = st.empty()

    for i, ticker in enumerate(tickers):
        status.text(f"{i+1}/{len(tickers)}: {ticker}")
        res = analyze_stock(ticker, selected_signals)
        if res:
            results.append(res)
        progress.progress((i + 1) / len(tickers))

    if results:
        df = pd.DataFrame(results)
        save_results(df)
        st.success(f"{len(df)} Treffer gefunden")
        st.dataframe(df)
        with st.expander("📥 Ergebnisse als CSV herunterladen"):
            st.download_button("Download CSV", df.to_csv(index=False), file_name="screening_ergebnisse.csv")
    else:
        st.warning("Keine Treffer gefunden.")

# Statistik
st.subheader("📅 Statistiken aus den letzten 30 Tagen")
history_df = load_recent_stats()
if history_df.empty:
    st.info("Noch keine historischen Treffer gespeichert.")
else:
    count_by_day = history_df.groupby(history_df["Datum"].dt.date).size().reset_index(name="Anzahl Treffer")
    st.bar_chart(data=count_by_day, x="Datum", y="Anzahl Treffer")
