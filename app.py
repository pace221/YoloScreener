import streamlit as st
import pandas as pd
import screener

st.set_page_config(page_title="📈 YOLO Screener", layout="wide")

st.title("📈 YOLO Screener")

st.header("📊 Marktstatus")

# Abruf der Indizes
index_status = screener.get_index_status()

# Anzeige Index Status
cols = st.columns(2)
for idx, (name, data) in zip(range(2), index_status.items()):
    with cols[idx]:
        st.subheader(f"{name} Index")
        st.metric("Close", data["Close"])
        st.metric("EMA10", data["EMA10"])
        st.metric("EMA20", data["EMA20"])
        st.metric("EMA200", data["EMA200"])

st.divider()

st.header("📋 Screening Ergebnisse")

if st.button("🚀 Screening starten"):
    df = screener.run_screening()
    if df.empty:
        st.warning("Keine Treffer gefunden.")
    else:
        st.dataframe(df, use_container_width=True)
