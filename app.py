import streamlit as st
import pandas as pd
from screener import (
    get_tickers,
    analyze_stock,
    get_index_status,
    save_results,
    load_recent_stats
)

st.set_page_config(page_title="YOLO Screener", layout="wide")
st.title("🚀 YOLO Screener")

st.subheader("📊 Marktstatus")

index_status = get_index_status()
cols = st.columns(2)
for i, (name, status) in enumerate(index_status.items()):
    with cols[i]:
        st.markdown(f"**{name}**")
        st.write(f"**Close:** {status['Close']}")
        for ema in ['EMA10', 'EMA20', 'EMA200']:
            val = status[ema]
            badge = "🟢" if val["Status"] == "über" else "🔴"
            st.write(f"{badge} {ema}: {val['Status']} ({val['Wert']})")

st.markdown("---")
st.subheader("📌 Signale")

all_signals = [
    "EMA Reclaim",
    "Breakout 20d High",
    "RSI > 60",
    "Volumen-Breakout",
    "Inside Day",
    "Cup-with-Handle",
    "SFP"
]

col1, col2 = st.columns([3, 1])
with col1:
    selected_signals = st.multiselect(
        "Signale auswählen",
        all_signals,
        default=[]
    )
with col2:
    if st.button("Alle auswählen"):
        selected_signals = all_signals

mode = st.radio("Verknüpfung:", ["ODER", "UND"])

if not selected_signals:
    st.warning("Bitte mind. ein Signal wählen.")
    st.stop()

if st.button("🔍 Screening starten"):
    tickers = get_tickers()
    results = []
    progress = st.progress(0)

    for idx, ticker in enumerate(tickers):
        res = analyze_stock(ticker, selected_signals, mode)
        if res:
            results.append(res)
        progress.progress((idx + 1) / len(tickers))

    if results:
        df = pd.DataFrame(results)
        st.success(f"{len(df)} Treffer gefunden.")
        st.dataframe(df)
        save_results(df)
    else:
        st.info("Keine Treffer gefunden.")

st.subheader("📈 Statistik der letzten 30 Tage")
history_df = load_recent_stats(30)
if history_df.empty:
    st.info("Keine Daten vorhanden.")
else:
    grouped = history_df.groupby(["Signals Detected", "Ticker"]).size().reset_index(name="Treffer")
    st.dataframe(grouped)
