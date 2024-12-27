import pandas as pd
import argparse

def analizar_matriz(csv_path, umbral):
    df = pd.read_csv(csv_path)
    criticos = df[df['Prioridad de Implementación'] == 'Alta']
    dependencias = criticos['Tecnología/Sistema'].value_counts()
    críticos_filtrados = dependencias[dependencias >= umbral]
    if not críticos_filtrados.empty:
        print("Alerta: Se han detectado dependencias críticas.")
        exit(1)
    else:
        print("Validación exitosa. No se detectaron dependencias críticas.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Analizar matriz de dependencias.')
    parser.add_argument('--csv', type=str, required=True, help='Ruta al archivo CSV')
    parser.add_argument('--umbral', type=int, required=True, help='Umbral de dependencias críticas')
    args = parser.parse_args()
    analizar_matriz(args.csv, args.umbral)
