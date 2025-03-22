# Documentación del Proceso de Limpieza de Datos

Este documento describe el proceso de limpieza y preprocesamiento de datos para el proyecto "Ruleta de la Vida".

## Índice

1. [Visión General](#visión-general)
2. [Fuentes de Datos](#fuentes-de-datos)
3. [Proceso de Limpieza](#proceso-de-limpieza)
4. [Transformaciones Aplicadas](#transformaciones-aplicadas)
5. [Problemas Encontrados y Soluciones](#problemas-encontrados-y-soluciones)
6. [Estructura de Datos Final](#estructura-de-datos-final)
7. [Instrucciones de Uso](#instrucciones-de-uso)

## Visión General

El objetivo de este proceso es migrar datos desde archivos Excel a un formato CSV, limpiarlos y preprocesarlos para su uso en el análisis y visualización dentro de la aplicación "Ruleta de la Vida". El proceso incluye la conversión de formatos, limpieza de datos, manejo de valores faltantes, normalización de categorías y validación de datos.

## Fuentes de Datos

Los datos originales provienen de archivos Excel con la siguiente estructura:

- **Archivo 1**: [Descripción del contenido, estructura y propósito]
- **Archivo 2**: [Descripción del contenido, estructura y propósito]
- ...

## Proceso de Limpieza

El proceso de limpieza se realizó utilizando scripts de Python y se dividió en las siguientes etapas:

1. **Conversión de Excel a CSV**: Utilizando el script `excel_to_csv.py` para convertir los archivos Excel originales a formato CSV.
2. **Limpieza y Preprocesamiento**: Utilizando el script `data_cleaning.py` para limpiar y preprocesar los datos.
3. **Combinación de Datos**: Utilizando el script `merge_csv.py` para combinar múltiples archivos CSV en un único archivo `data.csv`.

### Pasos Detallados

#### 1. Conversión de Excel a CSV

```bash
python data_processing/excel_to_csv.py datos_originales.xlsx --output datos_originales.csv

