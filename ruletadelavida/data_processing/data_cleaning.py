"""
Script para limpiar y preprocesar datos.
Este script toma un archivo CSV, realiza limpieza y preprocesamiento, y guarda los datos limpios.
"""

import pandas as pd
import numpy as np
import os
import argparse
import re
from datetime import datetime

def clean_data(input_file="processed/respuestas_ruleta_vida.csv", output_file=None):
    """
    Limpia y preprocesa un archivo CSV.
    
    Args:
        input_file (str): Ruta al archivo CSV de entrada.
        output_file (str, optional): Ruta al archivo CSV de salida. Si no se proporciona,
                                    se usará 'data.csv' en el directorio actual.
    
    Returns:
        pandas.DataFrame: DataFrame con los datos limpios.
    """
    try:
        # Verificar que el archivo de entrada existe
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"El archivo {input_file} no existe.")
        
        # Leer el archivo CSV
        print(f"Leyendo archivo CSV: {input_file}")
        df = pd.read_csv(input_file)
        
        # Guardar una copia de los datos originales para comparación
        df_original = df.copy()
        
        # Mostrar información inicial
        print("\nInformación inicial del DataFrame:")
        print(f"Filas: {df.shape[0]}")
        print(f"Columnas: {df.shape[1]}")
        print(f"Columnas: {', '.join(df.columns.tolist())}")
        
        # 1. Limpieza de nombres de columnas
        df.columns = [clean_column_name(col) for col in df.columns]
        
        # 2. Eliminar filas duplicadas
        duplicates = df.duplicated()
        if duplicates.any():
            print(f"\nEliminando {duplicates.sum()} filas duplicadas.")
            df = df.drop_duplicates().reset_index(drop=True)
        
        # 3. Manejar valores faltantes
        missing_values = df.isnull().sum()
        if missing_values.any():
            print("\nValores faltantes por columna:")
            for col, count in missing_values[missing_values > 0].items():
                print(f"  {col}: {count} ({count/len(df):.2%})")
            
            # Estrategia para manejar valores faltantes
            df = handle_missing_values(df)
        
        # 4. Convertir tipos de datos
        df = convert_data_types(df)
        
        # 5. Limpieza específica para cada columna
        df = clean_columns(df)
        
        # 6. Validación de datos
        df = validate_data(df)
        
        # Mostrar información después de la limpieza
        print("\nInformación después de la limpieza:")
        print(f"Filas: {df.shape[0]}")
        print(f"Columnas: {df.shape[1]}")
        
        # Mostrar cambios realizados
        print("\nResumen de cambios:")
        print(f"Filas originales: {df_original.shape[0]}")
        print(f"Filas después de limpieza: {df.shape[0]}")
        print(f"Filas eliminadas: {df_original.shape[0] - df.shape[0]}")
        
        # Si no se proporciona un nombre de archivo de salida, usar 'data.csv'
        if output_file is None:
            output_file = "data.csv"
        
        # Guardar datos limpios
        df.to_csv(output_file, index=False, encoding='utf-8')
        print(f"\nDatos limpios guardados como: {output_file}")
        
        return df
    
    except Exception as e:
        print(f"Error al limpiar los datos: {str(e)}")
        raise

def clean_column_name(column_name):
    """
    Limpia y estandariza un nombre de columna.
    
    Args:
        column_name (str): Nombre de columna original.
    
    Returns:
        str: Nombre de columna limpio.
    """
    # Convertir a minúsculas
    column_name = column_name.lower()
    
    # Reemplazar espacios y caracteres especiales con guiones bajos
    column_name = re.sub(r'[^a-z0-9]', '_', column_name)
    
    # Eliminar guiones bajos múltiples
    column_name = re.sub(r'_+', '_', column_name)
    
    # Eliminar guiones bajos al principio y al final
    column_name = column_name.strip('_')
    
    return column_name

def handle_missing_values(df):
    """
    Maneja los valores faltantes en el DataFrame.
    
    Args:
        df (pandas.DataFrame): DataFrame con valores faltantes.
    
    Returns:
        pandas.DataFrame: DataFrame con valores faltantes manejados.
    """
    # Estrategia para cada tipo de columna
    for col in df.columns:
        missing_count = df[col].isnull().sum()
        if missing_count == 0:
            continue
        
        # Si es una columna numérica, rellenar con la mediana
        if pd.api.types.is_numeric_dtype(df[col]):
            median_value = df[col].median()
            df[col] = df[col].fillna(median_value)
            print(f"  Columna '{col}': {missing_count} valores faltantes rellenados con la mediana ({median_value})")
        
        # Si es una columna de fecha, rellenar con la fecha más frecuente
        elif pd.api.types.is_datetime64_dtype(df[col]):
            mode_value = df[col].mode()[0]
            df[col] = df[col].fillna(mode_value)
            print(f"  Columna '{col}': {missing_count} valores faltantes rellenados con la moda ({mode_value})")
        
        # Si es una columna categórica o de texto, rellenar con la moda
        else:
            # Si todos los valores son nulos, rellenar con 'Desconocido'
            if missing_count == len(df):
                df[col] = df[col].fillna('Desconocido')
                print(f"  Columna '{col}': {missing_count} valores faltantes rellenados con 'Desconocido'")
            else:
                mode_value = df[col].mode()[0]
                df[col] = df[col].fillna(mode_value)
                print(f"  Columna '{col}': {missing_count} valores faltantes rellenados con la moda ({mode_value})")
    
    return df

def convert_data_types(df):
    """
    Convierte los tipos de datos de las columnas.
    
    Args:
        df (pandas.DataFrame): DataFrame original.
    
    Returns:
        pandas.DataFrame: DataFrame con tipos de datos convertidos.
    """
    # Intentar convertir columnas a tipos de datos apropiados
    for col in df.columns:
        # Intentar convertir a numérico si parece ser numérico
        if df[col].dtype == 'object':
            # Verificar si la columna parece contener fechas
            if is_date_column(df[col]):
                try:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
                    print(f"  Columna '{col}' convertida a tipo fecha")
                except:
                    pass
            # Verificar si la columna parece contener números
            elif is_numeric_column(df[col]):
                try:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                    print(f"  Columna '{col}' convertida a tipo numérico")
                except:
                    pass
    
    return df

def is_date_column(series):
    """
    Verifica si una serie parece contener fechas.
    
    Args:
        series (pandas.Series): Serie a verificar.
    
    Returns:
        bool: True si la serie parece contener fechas, False en caso contrario.
    """
    # Tomar una muestra de valores no nulos
    sample = series.dropna().sample(min(10, len(series.dropna())))
    
    # Intentar convertir la muestra a fechas
    try:
        pd.to_datetime(sample, errors='raise')
        return True
    except:
        return False

def is_numeric_column(series):
    """
    Verifica si una serie parece contener valores numéricos.
    
    Args:
        series (pandas.Series): Serie a verificar.
    
    Returns:
        bool: True si la serie parece contener valores numéricos, False en caso contrario.
    """
    # Tomar una muestra de valores no nulos
    sample = series.dropna().sample(min(10, len(series.dropna())))
    
    # Intentar convertir la muestra a numérico
    try:
        pd.to_numeric(sample, errors='raise')
        return True
    except:
        return False

def clean_columns(df):
    """
    Realiza limpieza específica para cada columna.
    
    Args:
        df (pandas.DataFrame): DataFrame original.
    
    Returns:
        pandas.DataFrame: DataFrame con columnas limpias.
    """
    # Aquí puedes agregar limpieza específica para cada columna
    # Por ejemplo, normalizar categorías, corregir errores comunes, etc.
    
    # Ejemplo: normalizar valores de sexo
    if 'sexo' in df.columns:
        # Convertir a minúsculas
        df['sexo'] = df['sexo'].str.lower()
        
        # Normalizar valores
        sexo_mapping = {
            'm': 'masculino',
            'f': 'femenino',
            'h': 'masculino',
            'v': 'masculino',
            'mujer': 'femenino',
            'hombre': 'masculino',
            'varon': 'masculino',
            'femenina': 'femenino',
            'masculina': 'masculino'
        }
        
        # Aplicar mapeo solo a valores que están en el diccionario
        df['sexo'] = df['sexo'].apply(lambda x: sexo_mapping.get(x, x) if pd.notna(x) else x)
        print("  Columna 'sexo' normalizada")
    
    # Ejemplo: normalizar valores de estado civil
    if 'estado_civil' in df.columns:
        # Convertir a minúsculas
        df['estado_civil'] = df['estado_civil'].str.lower()
        
        # Normalizar valores
        estado_civil_mapping = {
            's': 'soltero',
            'c': 'casado',
            'd': 'divorciado',
            'v': 'viudo',
            'u': 'union libre',
            'ul': 'union libre',
            'soltero/a': 'soltero',
            'casado/a': 'casado',
            'divorciado/a': 'divorciado',
            'viudo/a': 'viudo'
        }
        
        # Aplicar mapeo solo a valores que están en el diccionario
        df['estado_civil'] = df['estado_civil'].apply(lambda x: estado_civil_mapping.get(x, x) if pd.notna(x) else x)
        print("  Columna 'estado_civil' normalizada")
    
    # Ejemplo: limpiar valores de calificación
    for col in df.columns:
        if 'calificacion' in col or 'puntuacion' in col:
            # Asegurarse de que las calificaciones estén en el rango 1-10
            if pd.api.types.is_numeric_dtype(df[col]):
                # Identificar valores fuera de rango
                out_of_range = ((df[col] < 1) | (df[col] > 10)) & df[col].notna()
                if out_of_range.any():
                    print(f"  Columna '{col}': {out_of_range.sum()} valores fuera de rango corregidos")
                    
                    # Corregir valores fuera de rango
                    df.loc[df[col] < 1, col] = 1
                    df.loc[df[col] > 10, col] = 10
    
    return df

def validate_data(df):
    """
    Valida los datos y elimina filas con valores inválidos.
    
    Args:
        df (pandas.DataFrame): DataFrame a validar.
    
    Returns:
        pandas.DataFrame: DataFrame validado.
    """
    # Validar edades (si existe la columna)
    if 'edad' in df.columns and pd.api.types.is_numeric_dtype(df['edad']):
        # Identificar edades inválidas (por ejemplo, negativas o mayores a 120)
        invalid_ages = (df['edad'] < 0) | (df['edad'] > 120)
        if invalid_ages.any():
            print(f"  Eliminando {invalid_ages.sum()} filas con edades inválidas")
            df = df[~invalid_ages].reset_index(drop=True)
    
    # Validar fechas (si existen columnas de fecha)
    for col in df.columns:
        if pd.api.types.is_datetime64_dtype(df[col]):
            # Identificar fechas futuras (si no deberían existir)
            future_dates = df[col] > pd.Timestamp.now()
            if future_dates.any():
                print(f"  Columna '{col}': {future_dates.sum()} fechas futuras detectadas")
                # Aquí puedes decidir qué hacer con las fechas futuras
                # Por ejemplo, establecerlas a la fecha actual o eliminar las filas
    
    # Validar valores categóricos (si existen columnas categóricas)
    # Por ejemplo, verificar que los valores de sexo sean válidos
    if 'sexo' in df.columns:
        valid_sexes = ['masculino', 'femenino', 'otro']
        invalid_sexes = ~df['sexo'].isin(valid_sexes) & df['sexo'].notna()
        if invalid_sexes.any():
            print(f"  Columna 'sexo': {invalid_sexes.sum()} valores inválidos")
            # Aquí puedes decidir qué hacer con los valores inválidos
            # Por ejemplo, establecerlos a 'otro' o eliminar las filas
            df.loc[invalid_sexes, 'sexo'] = 'otro'
    
    return df

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Limpia y preprocesa un archivo CSV.')
    parser.add_argument('input', help='Archivo CSV de entrada')
    parser.add_argument('--output', help='Archivo CSV de salida (por defecto: data.csv)')
    
    args = parser.parse_args()
    
    clean_data(args.input, args.output)

