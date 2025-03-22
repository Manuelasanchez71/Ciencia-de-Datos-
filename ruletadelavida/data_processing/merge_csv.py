"""
Script para combinar múltiples archivos CSV en uno solo.
Este script toma varios archivos CSV y los combina en un único archivo.
"""

import pandas as pd
import os
import argparse
import glob

def merge_csv_files(input_files="data/clean/respuestas_ruleta_vida_clean.csv", output_file='data.csv', how='outer'):
    """
    Combina múltiples archivos CSV en uno solo.
    
    Args:
        input_files (list): Lista de rutas a los archivos CSV de entrada.
        output_file (str, optional): Ruta al archivo CSV de salida. Por defecto es 'data.csv'.
        how (str, optional): Tipo de unión a realizar ('inner', 'outer', 'left', 'right'). Por defecto es 'outer'.
    
    Returns:
        pandas.DataFrame: DataFrame combinado.
    """
    try:
        if not input_files:
            raise ValueError("No se proporcionaron archivos de entrada.")
        
        print(f"Combinando {len(input_files)} archivos CSV...")
        
        # Leer el primer archivo
        df_combined = pd.read_csv(input_files[0])
        print(f"Leyendo {input_files[0]}: {df_combined.shape[0]} filas, {df_combined.shape[1]} columnas")
        
        # Combinar con los archivos restantes
        for file in input_files[1:]:
            df = pd.read_csv(file)
            print(f"Leyendo {file}: {df.shape[0]} filas, {df.shape[1]} columnas")
            
            # Identificar columnas comunes para la unión
            common_columns = set(df_combined.columns) & set(df.columns)
            if not common_columns:
                print(f"Advertencia: No hay columnas comunes entre {input_files[0]} y {file}.")
                print(f"Concatenando archivos en lugar de unirlos...")
                df_combined = pd.concat([df_combined, df], ignore_index=True)
            else:
                # Unir DataFrames
                df_combined = pd.merge(df_combined, df, how=how, on=list(common_columns))
        
        # Guardar el DataFrame combinado
        df_combined.to_csv(output_file, index=False, encoding='utf-8')
        print(f"\nArchivos combinados guardados como: {output_file}")
        print(f"Dimensiones finales: {df_combined.shape[0]} filas, {df_combined.shape[1]} columnas")
        
        return df_combined
    
    except Exception as e:
        print(f"Error al combinar archivos CSV: {str(e)}")
        raise

def find_csv_files(directory):
    """
    Encuentra todos los archivos CSV en un directorio.
    
    Args:
        directory (str): Directorio donde buscar archivos CSV.
    
    Returns:
        list: Lista de rutas a los archivos CSV encontrados.
    """
    if not os.path.isdir(directory):
        raise NotADirectoryError(f"{directory} no es un directorio válido.")
    
    csv_files = glob.glob(os.path.join(directory, "*.csv"))
    
    if not csv_files:
        print(f"No se encontraron archivos CSV en {directory}")
    
    return csv_files

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Combina múltiples archivos CSV en uno solo.')
    parser.add_argument('--input', nargs='+', help='Archivos CSV de entrada o directorio que contiene archivos CSV')
    parser.add_argument('--output', default='data.csv', help='Archivo CSV de salida (por defecto: data.csv)')
    parser.add_argument('--how', default='outer', choices=['inner', 'outer', 'left', 'right'],
                        help='Tipo de unión a realizar (por defecto: outer)')
    
    args = parser.parse_args()
    
    # Verificar si se proporcionó un directorio o archivos individuales
    if len(args.input) == 1 and os.path.isdir(args.input[0]):
        input_files = find_csv_files(args.input[0])
    else:
        input_files = args.input
    
    if input_files:
        merge_csv_files(input_files, args.output, args.how)

