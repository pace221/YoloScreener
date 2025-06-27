import streamlit as st
import pandas as pd
import screener

st.set_page_config(page_title="YOLO Screener", layout="wide")

st.title("📈 YOLO Screener")

# ---------- Marktstatus ----------
st.header("📊 Marktstatus")

index_status = screener.get_index_status()

for index_name, status in index_status.items():
    st.subheader(f"**{index_name}**")
    st.write(f"**Close:** {status['Close']}")
    st.write(f"**EMA10:** {status['EMA10']} | Wert: {status['EMA10_value']}")
    st.write(f"**EMA20:** {status['EMA20']} | Wert: {status['EMA20_value']}")
    st.write(f"**EMA200:** {status['EMA200']} | Wert: {status['EMA200_value']}")

# ---------- Screening ----------
st.header("🚀 Screening starten")

if st.button("Jetzt Screening durchführen"):
    df = screener.run_screening()
    if not df.empty:
        st.success(f"✅ {len(df)} Treffer gefunden!")
        st.dataframe(df)
    else:
        st.warning("❌ Keine Treffer gefunden.")
