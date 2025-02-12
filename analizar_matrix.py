import pandas as pd
import argparse

def retrieve_coafi(csv_path, coafi_column):
    df = pd.read_csv(csv_path)
    coafi_data = df[coafi_column].dropna().unique()
    return coafi_data

def analizar_matriz(csv_path, umbral, coafi_column):
    df = pd.read_csv(csv_path)
    criticos = df[df['Prioridad de Implementación'] == 'Alta']
    dependencias = criticos['Tecnología/Sistema'].value_counts()
    críticos_filtrados = dependencias[dependencias >= umbral]
    coafi_data = retrieve_coafi(csv_path, coafi_column)
    if not críticos_filtrados.empty:
        print("Alerta: Se han detectado dependencias críticas.")
        print(f"Datos COAFI: {coafi_data}")
        exit(1)
    else:
        print("Validación exitosa. No se detectaron dependencias críticas.")
        print(f"Datos COAFI: {coafi_data}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Analizar matriz de dependencias.')
    parser.add_argument('--csv', type=str, required=True, help='Ruta al archivo CSV')
    parser.add_argument('--umbral', type=int, required=True, help='Umbral de dependencias críticas')
    parser.add_argument('--coafi', type=str, required=True, help='Nombre de la columna COAFI')
    args = parser.parse_args()
    analizar_matriz(args.csv, args.umbral, args.coafi)
