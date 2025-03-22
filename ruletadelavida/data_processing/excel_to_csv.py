"""
Script para convertir archivos Excel a CSV.
Este script toma un archivo Excel y lo convierte a formato CSV.
"""

import pandas as pd
import os
import argparse
from datetime import datetime

def excel_to_csv(input_file="data/row/respuestas_ruleta_vida.xlsx", output_file=None, sheet_name=0):
    """
    Convierte un archivo Excel a CSV.
    
    Args:
        input_file (str): Ruta al archivo Excel de entrada.
        output_file (str, optional): Ruta al archivo CSV de salida. Si no se proporciona,
                                    se usará el mismo nombre que el archivo de entrada con extensión .csv.
        sheet_name (str/int, optional): Nombre o índice de la hoja a convertir. Por defecto es la primera hoja (0).
    
    Returns:
        str: Ruta al archivo CSV generado.
    """
    try:
        # Verificar que el archivo de entrada existe
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"El archivo {input_file} no existe.")
        
        # Leer el archivo Excel
        print(f"Leyendo archivo Excel: {input_file}")
        df = pd.read_excel(input_file, sheet_name=sheet_name)
        
         # Definir carpeta de salida
        output_dir = "data/processed/"
        os.makedirs(output_dir, exist_ok=True)  # Crear la carpeta si no existe

        # Si no se proporciona un nombre de archivo de salida, crear uno
        if output_file is None:
            base_name = os.path.splitext(input_file)[0]
            output_file = f"{base_name}.csv"
        
        # Guardar como CSV
        df.to_csv(output_file, index=False, encoding='utf-8')
        print(f"Archivo CSV guardado como: {output_file}")
        
        # Mostrar información sobre los datos
        print(f"\nInformación del DataFrame:")
        print(f"Filas: {df.shape[0]}")
        print(f"Columnas: {df.shape[1]}")
        print(f"Columnas: {', '.join(df.columns.tolist())}")
        
        return output_file
    
    except Exception as e:
        print(f"Error al convertir el archivo Excel a CSV: {str(e)}")
        raise

def process_directory(input_dir, output_dir=None):
    """
    Procesa todos los archivos Excel en un directorio y los convierte a CSV.
    
    Args:
        input_dir (str): Directorio que contiene los archivos Excel.
        output_dir (str, optional): Directorio donde se guardarán los archivos CSV.
                                   Si no se proporciona, se usará el mismo directorio de entrada.
    
    Returns:
        list: Lista de rutas a los archivos CSV generados.
    """
    if not os.path.isdir(input_dir):
        raise NotADirectoryError(f"{input_dir} no es un directorio válido.")
    
    if output_dir is None:
        output_dir = input_dir
    else:
        os.makedirs(output_dir, exist_ok=True)
    
    excel_files = [f for f in os.listdir(input_dir) if f.endswith(('.xlsx', '.xls'))]
    
    if not excel_files:
        print(f"No se encontraron archivos Excel en {input_dir}")
        return []
    
    csv_files = []
    for excel_file in excel_files:
        input_path = os.path.join(input_dir, excel_file)
        output_path = os.path.join(output_dir, os.path.splitext(excel_file)[0] + '.csv')
        
        try:
            csv_file = excel_to_csv(input_path, output_path)
            csv_files.append(csv_file)
        except Exception as e:
            print(f"Error al procesar {excel_file}: {str(e)}")
    
    return csv_files

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convierte archivos Excel a CSV.')
    parser.add_argument('input', help='Archivo Excel o directorio de entrada')
    parser.add_argument('--output', help='Archivo CSV o directorio de salida')
    parser.add_argument('--sheet', default=0, help='Nombre o índice de la hoja (por defecto: 0)')
    
    args = parser.parse_args()
    
    if os.path.isdir(args.input):
        # Procesar directorio
        process_directory(args.input, args.output)
    else:
        # Procesar archivo individual
        excel_to_csv(args.input, args.output, args.sheet)

