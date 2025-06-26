import streamlit as st
from screener import get_tickers, analyze_stock, get_index_status
from export_pdf import export_to_pdf
import pandas as pd
import yfinance as yf

st.set_page_config(layout="wide")
st.title("📊 Trading Screener – Long Setups (S&P500 & NASDAQ)")

# 📈 Marktstatus
st.subheader("📈 Marktstatus")

index_status = get_index_status()
for index, status in index_status.items():
    st.markdown(f"**{index} Status:**")
    cols = st.columns(3)
    for i, (ema, val) in enumerate(status.items()):
        if val == "über":
            cols[i].success(f"{ema}: über")
        elif val == "unter":
            cols[i].error(f"{ema}: unter")
        else:
            cols[i].warning(f"{ema}: n/a")

# ℹ️ Erklärung Signale (ausklappbar)
with st.expander("ℹ️ Erklärung der Signalsuche & Kriterien", expanded=False):
    st.markdown("""
    Das System screent alle im S&P 500 und NASDAQ 100 enthaltenen Aktien täglich auf folgende **Long-Signale**:

    ### ✅ Verwendete Signal-Kriterien

    - **EMA Reclaim**  
      Der Schlusskurs überwindet den EMA10 oder EMA20 nach einem Tag darunter.  
      _Hinweis: Trendfortsetzungs- oder Umkehrsignal._

    - **Breakout 20-Tages-Hoch**  
      Kurs bricht über den höchsten Stand der letzten 20 Handelstage.

    - **Cup-with-Handle**  
      Klassische Bodenformation mit Ausbruch nach Konsolidierung.

    - **SFP (Swing Failure Pattern)**  
      Unterschreiten vorheriger Tiefs mit starkem Rebound – häufig als Fehlausbruch gewertet.

    - **Inside Day Breakout**  
      Tageskerze vollständig innerhalb der Vortageskerze → Ausbruch über das Hoch gilt als Einstieg.

    - **RSI > 60**  
      Relative Stärke vorhanden, oft Filter zur Bestätigung des Trends.

    - **Volumen-Breakout**  
      Tagesvolumen liegt über dem 20-Tage-Durchschnitt, was auf institutionelles Interesse hindeutet.

    ### 📊 Nur Aktien, die **mindestens ein Signal** erfüllen, werden angezeigt.
    """)

    st.image("https://raw.githubusercontent.com/public-quant/visuals/main/ema_reclaim.png", 
             caption="📈 Beispiel: EMA20-Reclaim mit steigendem Volumen", use_container_width=True)

    st.image("https://raw.githubusercontent.com/public-quant/visuals/main/cup_handle.png", 
             caption="🏆 Beispiel: Cup-with-Handle-Formation mit Breakout", use_container_width=True)

    st.image("https://raw.githubusercontent.com/public-quant/visuals/main/inside_day_breakout.png", 
             caption="📉 Beispiel: Inside Day mit Ausbruch über das Vortageshoch", use_container_width=True)

st.markdown("---")

# 🚀 Screener starten
if st.button("Screening starten"):
    tickers = get_tickers()  # Alle Ticker prüfen (~518)
    results = []
    progress = st.progress(0)
    status_text = st.empty()

    for i, ticker in enumerate(tickers):
        status_text.text(f"🔍 Analysiere {ticker} ({i + 1} von {len(tickers)})")
        res = analyze_stock(ticker)
        if res:
            results.append(res)
        progress.progress((i + 1) / len(tickers))

    df = pd.DataFrame(results)

    if df.empty:
        st.warning("Keine Setups gefunden.")
    else:
        # 📅 Analyse-Datum anzeigen
        latest_data = None
        for ticker in df["Ticker"]:
            try:
                hist = yf.download(ticker, period="5d", interval="1d", progress=False)
                if not hist.empty:
                    latest_data = hist.index[-1].strftime("%Y-%m-%d")
                    break
            except:
                continue

        if latest_data:
            st.info(f"📅 Screening-Basis: Schlusskurs vom **{latest_data}**")

        st.success(f"{len(df)} gültige Setups gefunden!")
        df_show = df.drop(columns=["KO-Link"])
        st.dataframe(df_show)

        # 📄 PDF exportieren
        export_to_pdf(df)
        with open("trading_signale.pdf", "rb") as f:
            st.download_button("📥 PDF herunterladen", f, file_name="trading_signale.pdf")

        # 🔗 KO-Produkte anzeigen
        st.markdown("---")
        st.subheader("🔎 KO-Produkte (OnVista)")
        for _, row in df.iterrows():
            st.markdown(f"• [{row['Ticker']}: KO-Link öffnen]({row['KO-Link']})", unsafe_allow_html=True)
