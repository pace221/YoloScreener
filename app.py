import streamlit as st
from screener import (
    get_tickers,
    analyze_stock,
    get_index_status,
    load_recent_stats,
    save_results
)
from export_pdf import export_to_pdf
import pandas as pd
import yfinance as yf

st.set_page_config(layout="wide")
st.title("📊 Trading Screener – Long Setups (S&P500 & NASDAQ)")

# 📈 Marktstatus anzeigen
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

# 🛠️ Signalfilter-Auswahl
st.markdown("---")
st.subheader("🛠️ Signalfilter auswählen")

default_signals = [
    "EMA Reclaim",
    "Breakout 20d High",
    "Cup-with-Handle",
    "SFP",
    "Inside Day",
    "RSI > 60",
    "Volumen-Breakout"
]

if "select_all" not in st.session_state:
    st.session_state.select_all = False

if st.button("✅ Alle Signale auswählen"):
    st.session_state.select_all = True

selected_signals = []
for signal in default_signals:
    if st.checkbox(signal, value=st.session_state.select_all):
        selected_signals.append(signal)

# ℹ️ Erklärung der Signalsuche
with st.expander("ℹ️ Erklärung der Signalsuche & Kriterien", expanded=False):
    st.markdown("""
    Das System screent alle im S&P 500 und NASDAQ 100 enthaltenen Aktien täglich auf folgende **Long-Signale**:

    ### ✅ Verwendete Signal-Kriterien

    - **EMA Reclaim**: Schlusskurs über EMA10 oder EMA20 nach einem Tag darunter.
    - **Breakout 20-Tages-Hoch**: Kurs bricht über den höchsten Stand der letzten 20 Handelstage.
    - **Cup-with-Handle**: Bodenformation mit Ausbruch nach Konsolidierung.
    - **SFP**: Tief wird unterboten, Schlusskurs erholt sich über vorheriges Close.
    - **Inside Day**: Aktueller Tageskerzenkörper vollständig innerhalb der Vortageskerze.
    - **RSI > 60**: Momentum-Filter zur Trendbestätigung.
    - **Volumen-Breakout**: Tagesvolumen über 20-Tage-Durchschnitt.

    _Nur Long-Signale werden berücksichtigt._
    """)

# 🚀 Screening starten
st.markdown("---")
if st.button("Screening starten"):
    if not selected_signals:
        st.warning("Bitte wähle mindestens ein Signal aus.")
    else:
        tickers = get_tickers()
        results = []
        progress = st.progress(0)
        status_text = st.empty()

        for i, ticker in enumerate(tickers):
            status_text.text(f"🔍 Analysiere {ticker} ({i + 1} von {len(tickers)})")
            res = analyze_stock(ticker, selected_signals)
            if res:
                results.append(res)
            progress.progress((i + 1) / len(tickers))

        df = pd.DataFrame(results)

        if df.empty:
            st.warning("Keine Setups gefunden.")
        else:
            # 📅 Datum der Kursdaten anzeigen
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

            # Ergebnisse anzeigen
            df_show = df.drop(columns=["KO-Link"])
            st.dataframe(df_show)

            # Ergebnisse speichern
            save_results(df)

            # PDF Export
            export_to_pdf(df)
            with open("trading_signale.pdf", "rb") as f:
                st.download_button("📥 PDF herunterladen", f, file_name="trading_signale.pdf")

            # KO-Produkte anzeigen
            st.markdown("---")
            st.subheader("🔎 KO-Produkte (OnVista)")
            for _, row in df.iterrows():
                st.markdown(f"• [{row['Ticker']}: KO-Link öffnen]({row['KO-Link']})", unsafe_allow_html=True)

# 📊 Statistik: Letzte 30 Tage
st.markdown("---")
st.subheader("📊 Statistik: Treffer der letzten 30 Tage")

stats_df = load_recent_stats()

if stats_df.empty:
    st.info("Noch keine Historie verfügbar.")
else:
    # Treffer pro Tag
    treffer_pro_tag = stats_df.groupby("Datum").size().reset_index(name="Anzahl")
    st.line_chart(treffer_pro_tag.set_index("Datum"))

    # Häufigste Signale
    signal_stats = stats_df["Signals Detected"].str.get_dummies(sep=", ").sum().sort_values(ascending=False)
    st.bar_chart(signal_stats)
