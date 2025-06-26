    from fpdf import FPDF
    
    def export_to_pdf(df, filename="trading_signale.pdf"):
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font("Arial", size=10)
        pdf.cell(200, 10, txt="📈 Trading Signale – Long Setups", ln=True, align='C')
    
        for idx, row in df.iterrows():
            pdf.cell(200, 8, ln=True)
            for col in df.columns:
                if "KO-Link" in col:
                    continue  # KO-Link nicht ins PDF schreiben
                value = str(row[col])
                pdf.cell(200, 6, txt=f"{col}: {value}", ln=True)
    
        pdf.output(filename)
