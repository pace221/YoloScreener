import streamlit as st
import pandas as pd
import screener

st.set_page_config(page_title="YOLO Screener", layout="wide")

st.title("📈 YOLO Screener")

st.header("📊 Marktstatus")

index_status = screener.get_index_status()

for ticker, stats in index_status.items():
    st.subheader(f"{ticker}")
    st.write(
        f"**Close:** {stats['Close']}, "
        f"**EMA10:** {stats['EMA10']} ({stats['EMA10_value']}), "
        f"**EMA20:** {stats['EMA20']} ({stats['EMA20_value']}), "
        f"**EMA200:** {stats['EMA200']} ({stats['EMA200_value']})"
    )

st.header("🕵️ Screening Ergebnisse")

if st.button("Screening starten"):
    df = screener.run_screening()
    st.dataframe(df)
