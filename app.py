import streamlit as st
from screener import run_screening, get_index_status
from export_pdf import export_to_pdf

st.set_page_config(layout="wide")
st.title("📊 Trading Screener – Long Setups (S&P500 & NASDAQ)")

# 🧭 Marktstatus (SPY & QQQ)
index_status = get_index_status()

st.subheader("📈 Marktstatus")

for index, status in index_status.items():
    st.markdown(f"**{index} Status:**")
    cols = st.columns(3)
    for i, (ema, val) in enumerate(status.items()):
        if val == "über":
            cols[i].success(f"{ema}: über")
        else:
            cols[i].error(f"{ema}: unter")

st.markdown("---")

# 🚀 Screener starten
if st.button("Screening starten"):
    with st.spinner("Lade Markt-Daten..."):
        df = run_screening()
        if df.empty:
            st.warning("Keine Setups gefunden.")
        else:
            st.success(f"{len(df)} gültige Setups gefunden!")
            df_show = df.drop(columns=["KO-Link"])
            st.dataframe(df_show)

            # 📄 PDF-Export
            export_to_pdf(df)
            with open("trading_signale.pdf", "rb") as f:
                st.download_button("📥 PDF herunterladen", f, file_name="trading_signale.pdf")

            # 🔗 KO-Links anzeigen
            st.markdown("---")
            for i, row in df.iterrows():
                st.markdown(f"🔎 [KO-Produkte für {row['Ticker']}]({row['KO-Link']})", unsafe_allow_html=True)
