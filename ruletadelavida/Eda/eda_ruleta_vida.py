# Paso 1: Instalación de bibliotecas necesarias
# pip install pandas numpy matplotlib seaborn

# Paso 2: Importación de librerías y carga de datos
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta

# Configuración para visualizaciones más atractivas
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("Blues_r")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 12

print("=== ANÁLISIS EXPLORATORIO DE DATOS - RULETA DE LA VIDA ===\n")

# Cargar el conjunto de datos (o generar datos de ejemplo si no existe)
try:
    print("Intentando cargar datos desde CSV...")
    data = pd.read_csv('datos_ruleta_vida_ejemplo.csv')
    print("Datos cargados correctamente.")
except FileNotFoundError:
    print("Archivo CSV no encontrado. Generando datos de ejemplo...")
    
    # Generar datos de ejemplo
    np.random.seed(42)
    n_respuestas = 100
    
    # Crear datos demográficos
    edades = np.random.randint(18, 70, n_respuestas)
    sexos = np.random.choice(['masculino', 'femenino'], n_respuestas)
    estados_civiles = np.random.choice(['soltero', 'casado', 'union libre', 'divorciado', 'viudo'], n_respuestas)
    
    # Crear fechas aleatorias en el último año
    fechas = [datetime.now() - timedelta(days=np.random.randint(1, 365)) for _ in range(n_respuestas)]
    
    # Crear dimensiones con valores aleatorios (con cierta correlación)
    base = np.random.normal(6, 1.5, n_respuestas)
    
    salud_y_bienestar = np.clip(base + np.random.normal(0, 1, n_respuestas), 1, 10)
    relaciones = np.clip(base + np.random.normal(0.5, 1, n_respuestas), 1, 10)
    carrera_y_proposito = np.clip(base + np.random.normal(-0.5, 1.2, n_respuestas), 1, 10)
    finanzas = np.clip(carrera_y_proposito + np.random.normal(0, 1, n_respuestas), 1, 10)
    desarrollo_personal = np.clip(base + np.random.normal(0.2, 1, n_respuestas), 1, 10)
    diversion_y_ocio = np.clip(salud_y_bienestar + np.random.normal(0, 1, n_respuestas), 1, 10)
    espiritualidad = np.clip(np.random.normal(5, 2, n_respuestas), 1, 10)
    entorno_fisico = np.clip(base + np.random.normal(0.3, 1, n_respuestas), 1, 10)
    
    # Crear DataFrame
    data = pd.DataFrame({
        'id': range(1, n_respuestas + 1),
        'usuario_id': np.random.randint(1, 30, n_respuestas),
        'fecha': fechas,
        'edad': edades,
        'sexo': sexos,
        'estado_civil': estados_civiles,
        'salud_y_bienestar': salud_y_bienestar,
        'relaciones': relaciones,
        'carrera_y_proposito': carrera_y_proposito,
        'finanzas': finanzas,
        'desarrollo_personal': desarrollo_personal,
        'diversion_y_ocio': diversion_y_ocio,
        'espiritualidad': espiritualidad,
        'entorno_fisico': entorno_fisico
    })
    
    # Guardar los datos generados
    data.to_csv('datos_ruleta_vida_ejemplo.csv', index=False)
    print("Datos de ejemplo generados y guardados en 'datos_ruleta_vida_ejemplo.csv'")

# Ver las primeras filas del conjunto de datos
print("\nPrimeras filas del conjunto de datos:")
print(data.head())

# Paso 3: Descripción general del conjunto de datos
print("\nDescripción general del conjunto de datos:")
print(data.describe())

# Definir las dimensiones para análisis
dimensiones = ['salud_y_bienestar', 'relaciones', 'carrera_y_proposito', 'finanzas', 
               'desarrollo_personal', 'diversion_y_ocio', 'espiritualidad', 'entorno_fisico']

# Paso 4: Identificación de valores atípicos
print("\nGenerando gráficos para identificar valores atípicos...")

# Boxplot para identificar valores atípicos en las dimensiones
plt.figure(figsize=(14, 8))
sns.boxplot(data=data[dimensiones])
plt.title("Boxplot de las dimensiones de la Ruleta de la Vida")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('boxplot_dimensiones.png')
plt.close()

# Paso 5: Visualización de la distribución de los datos (Histogramas)
print("Generando histogramas para visualizar la distribución de los datos...")

# Histogramas de las dimensiones
fig, axes = plt.subplots(2, 4, figsize=(16, 10))
axes = axes.flatten()

for i, dimension in enumerate(dimensiones):
    sns.histplot(data[dimension], bins=10, kde=True, ax=axes[i])
    axes[i].set_title(f'Distribución de {dimension}')
    axes[i].set_xlabel('Puntuación (1-10)')
    axes[i].set_ylabel('Frecuencia')

plt.tight_layout()
plt.savefig('histogramas_dimensiones.png')
plt.close()

# Histograma de edades
plt.figure(figsize=(10, 6))
sns.histplot(data['edad'], bins=10, kde=True)
plt.title('Distribución de edades de los usuarios')
plt.xlabel('Edad')
plt.ylabel('Frecuencia')
plt.savefig('histograma_edades.png')
plt.close()

# Paso 6: Relación entre las dimensiones (Gráficas de dispersión)
print("Generando gráficas de dispersión para analizar relaciones entre dimensiones...")

# Seleccionar un subconjunto de dimensiones para el pairplot (para no saturar el gráfico)
dimensiones_seleccionadas = ['salud_y_bienestar', 'relaciones', 'finanzas', 'desarrollo_personal']
sns.pairplot(data[dimensiones_seleccionadas + ['sexo']], hue='sexo')
plt.suptitle("Relaciones entre dimensiones por sexo", y=1.02)
plt.savefig('pairplot_dimensiones.png')
plt.close()

# Paso 7: Correlación entre dimensiones
print("Calculando y visualizando la matriz de correlación...")

# Calcular la matriz de correlación
correlation_matrix = data[dimensiones].corr()

# Mostrar la matriz de correlación con un mapa de calor
plt.figure(figsize=(12, 10))
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', linewidths=0.5)
plt.title("Mapa de calor de la correlación entre dimensiones")
plt.tight_layout()
plt.savefig('correlacion_dimensiones.png')
plt.close()

# Paso 8: Identificación de patrones
print("Identificando patrones en los datos...")

# Comparación de dimensiones por sexo
plt.figure(figsize=(14, 8))
for i, dimension in enumerate(dimensiones):
    plt.subplot(2, 4, i+1)
    sns.boxplot(x='sexo', y=dimension, data=data)
    plt.title(f'{dimension} por sexo')
    plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('dimensiones_por_sexo.png')
plt.close()

# Comparación de dimensiones por estado civil
plt.figure(figsize=(14, 10))
for i, dimension in enumerate(dimensiones):
    plt.subplot(2, 4, i+1)
    sns.boxplot(x='estado_civil', y=dimension, data=data)
    plt.title(f'{dimension} por estado civil')
    plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('dimensiones_por_estado_civil.png')
plt.close()

# Relación entre edad y dimensiones
plt.figure(figsize=(14, 10))
for i, dimension in enumerate(dimensiones):
    plt.subplot(2, 4, i+1)
    sns.scatterplot(x='edad', y=dimension, data=data, hue='sexo')
    plt.title(f'Edad vs {dimension}')
plt.tight_layout()
plt.savefig('edad_vs_dimensiones.png')
plt.close()

# Paso 9: Análisis de promedios por dimensión
print("Analizando promedios por dimensión...")

# Calcular promedios por dimensión
promedios = data[dimensiones].mean().sort_values(ascending=False)

plt.figure(figsize=(12, 6))
sns.barplot(x=promedios.index, y=promedios.values)
plt.title('Puntuación promedio por dimensión')
plt.xticks(rotation=45)
plt.ylabel('Puntuación promedio (1-10)')
plt.tight_layout()
plt.savefig('promedios_dimensiones.png')
plt.close()

# Paso 10: Análisis de la distribución de puntuaciones totales
print("Analizando la distribución de puntuaciones totales...")

# Calcular puntuación total para cada usuario
data['puntuacion_total'] = data[dimensiones].mean(axis=1)

plt.figure(figsize=(10, 6))
sns.histplot(data['puntuacion_total'], bins=20, kde=True)
plt.title('Distribución de puntuaciones totales')
plt.xlabel('Puntuación promedio (1-10)')
plt.ylabel('Frecuencia')
plt.savefig('distribucion_puntuacion_total.png')
plt.close()

# Paso 11: Análisis de tendencias temporales
print("Analizando tendencias temporales...")

# Convertir la columna de fecha a datetime si no lo está ya
if not pd.api.types.is_datetime64_any_dtype(data['fecha']):
    data['fecha'] = pd.to_datetime(data['fecha'])

# Extraer el mes y año
data['mes_año'] = data['fecha'].dt.to_period('M')

# Agrupar por mes y calcular promedios
tendencia_temporal = data.groupby('mes_año')[dimensiones].mean().reset_index()
tendencia_temporal['mes_año_str'] = tendencia_temporal['mes_año'].astype(str)

# Graficar tendencia temporal para cada dimensión
plt.figure(figsize=(14, 8))
for dimension in dimensiones:
    plt.plot(tendencia_temporal['mes_año_str'], tendencia_temporal[dimension], marker='o', label=dimension)

plt.title('Tendencia temporal de las dimensiones')
plt.xlabel('Mes y Año')
plt.ylabel('Puntuación promedio')
plt.xticks(rotation=45)
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.savefig('tendencia_temporal.png')
plt.close()

# Paso 12: Conclusiones del análisis exploratorio
print("\n=== CONCLUSIONES DEL ANÁLISIS EXPLORATORIO ===")

# Calcular estadísticas clave
dimension_mas_alta = promedios.index[0]
dimension_mas_baja = promedios.index[-1]
correlacion_mas_alta = correlation_matrix.unstack().sort_values(ascending=False).drop_duplicates().index[1]
correlacion_valor = correlation_matrix.unstack().sort_values(ascending=False).drop_duplicates().iloc[1]

print(f"\n1. Distribución de puntuaciones:")
print(f"   - La dimensión con mayor puntuación promedio es '{dimension_mas_alta}' con {promedios[dimension_mas_alta]:.2f}/10")
print(f"   - La dimensión con menor puntuación promedio es '{dimension_mas_baja}' con {promedios[dimension_mas_baja]:.2f}/10")
print(f"   - La puntuación total promedio es {data['puntuacion_total'].mean():.2f}/10")

print(f"\n2. Correlaciones entre dimensiones:")
print(f"   - La correlación más alta se encuentra entre {correlacion_mas_alta[0]} y {correlacion_mas_alta[1]} ({correlacion_valor:.2f})")
print(f"   - Esto sugiere que estas dimensiones tienden a moverse juntas")

print("\n3. Patrones demográficos:")
for dimension in dimensiones:
    promedio_hombres = data[data['sexo'] == 'masculino'][dimension].mean()
    promedio_mujeres = data[data['sexo'] == 'femenino'][dimension].mean()
    if abs(promedio_hombres - promedio_mujeres) > 0.5:
        print(f"   - Se observa una diferencia notable en '{dimension}' entre hombres ({promedio_hombres:.2f}) y mujeres ({promedio_mujeres:.2f})")

print("\n4. Valores atípicos:")
for dimension in dimensiones:
    q1 = data[dimension].quantile(0.25)
    q3 = data[dimension].quantile(0.75)
    iqr = q3 - q1
    outliers = data[(data[dimension] < q1 - 1.5 * iqr) | (data[dimension] > q3 + 1.5 * iqr)][dimension].count()
    if outliers > 0:
        print(f"   - Se identificaron {outliers} valores atípicos en la dimensión '{dimension}'")

print("\n5. Recomendaciones para análisis adicional:")
print("   - Investigar las razones detrás de la baja puntuación en la dimensión '" + dimension_mas_baja + "'")
print("   - Analizar más a fondo la relación entre " + correlacion_mas_alta[0] + " y " + correlacion_mas_alta[1])
print("   - Realizar un análisis de segmentación para identificar perfiles de usuarios")
print("   - Implementar modelos predictivos para estimar puntuaciones futuras")

# Guardar un resumen de los datos procesados
print("\nGuardando resumen de datos procesados...")
resumen = {
    'dimensiones': dimensiones,
    'promedios': promedios.to_dict(),
    'correlacion_matriz': correlation_matrix.to_dict(),
    'estadisticas': data[dimensiones].describe().to_dict()
}

import json
with open('resumen_analisis_exploratorio.json', 'w') as f:
    json.dump(resumen, f, indent=4, default=str)

print("\n=== ANÁLISIS EXPLORATORIO COMPLETADO ===")
print("Se han generado visualizaciones y archivos con los resultados")

