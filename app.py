import streamlit as st
import screener

st.set_page_config(page_title="YOLO Screener", layout="wide")

st.title("📈 YOLO Screener")

st.header("📊 Screening Ergebnisse")

if st.button("🔍 Screening starten"):
    st.info("Starte Screening, bitte etwas Geduld...")
    df = screener.run_screening()
    if df.empty:
        st.warning("Keine Treffer gefunden.")
    else:
        st.success(f"{len(df)} Treffer gefunden.")
        st.dataframe(df)
