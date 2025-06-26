from fpdf import FPDF
import pandas as pd

def export_to_pdf(df: pd.DataFrame, filename="trading_signale.pdf"):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, "Trading-Signale (S&P500 & NASDAQ Long Setups)", ln=True, align="C")
    pdf.ln(5)

    col_widths = [30, 50, 25, 25, 25, 25, 20, 25, 25, 25, 20, 50]
    columns = [
        "Ticker", "Name", "Entry (USD)", "Stop (USD)", "TP1", "TP2", "TP3",
        "CRV", "Qty (1R=100€)", "KO-Schwelle", "Abstand KO %", "Signals Detected"
    ]

    # Kopfzeile
    pdf.set_font("Arial", style='B', size=9)
    for i, col in enumerate(columns):
        w = col_widths[i] if i < len(col_widths) else 25
        pdf.cell(w, 8, col, border=1)
    pdf.ln()

    # Datenzeilen
    pdf.set_font("Arial", size=8)
    for _, row in df.iterrows():
        for i, col in enumerate(columns):
            w = col_widths[i] if i < len(col_widths) else 25
            val = str(row[col]) if col in row else "-"
            pdf.cell(w, 8, val, border=1)
        pdf.ln()

    pdf.output(filename)
