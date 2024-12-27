import pandas as pd
from fpdf import FPDF
import argparse

class PDFReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Reporte de Interdependencias Críticas', 0, 1, 'C')

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, title, 0, 1, 'L')
        self.ln(5)

    def chapter_body(self, body):
        self.set_font('Arial', '', 12)
        self.multi_cell(0, 10, body)
        self.ln()

def generar_reporte(csv_path, output):
    df = pd.read_csv(csv_path)
    pdf = PDFReport()
    pdf.add_page()
    pdf.chapter_title("Interdependencias Críticas")
    for index, row in df.iterrows():
        content = f"Tecnología/Sistema: {row['Tecnología/Sistema']}\nPrioridad: {row['Prioridad de Implementación']}\nEstado de Madurez: {row['Estado de Madurez']}\n"
        pdf.chapter_body(content)
    pdf.output(output)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generar reporte de interdependencias.')
    parser.add_argument('--csv', type=str, required=True, help='Ruta al archivo CSV')
    parser.add_argument('--output', type=str, required=True, help='Ruta de salida del reporte PDF')
    args = parser.parse_args()
    generar_reporte(args.csv, args.output)
