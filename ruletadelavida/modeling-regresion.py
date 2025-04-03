import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.linear_model import Ridge
from sklearn.cluster import KMeans
from sklearn.metrics import r2_score
import warnings

warnings.filterwarnings("ignore")

# === 1. Cargar datos ===
df = pd.read_csv(r"ruletadelavida/data/data.csv/merged_data.csv")

print("\n=== Datos Cargados ===\n")
print(df.head())

# === 2. Preprocesamiento ===
df_grouped = df.groupby(['usuario_id', 'edad', 'sexo', 'estado_civil']).agg({
    'calificacion': 'mean'
}).reset_index()

# Variables
X = df_grouped[['edad']]
y = df_grouped['calificacion']

# División
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

print("\n=== Datos Preparados ===\n")
print(X_train.head())

# === 3. Modelado Inicial ===
modelo = Ridge()
modelo.fit(X_train, y_train)
y_pred = modelo.predict(X_test)
r2_inicial = r2_score(y_test, y_pred)

print("\n=== Evaluación Inicial ===\n")
print(f"R² inicial: {r2_inicial:.4f}")

# 📊 Gráfico de dispersión inicial
plt.figure(figsize=(8, 6))
plt.scatter(y_test, y_pred, color='blue', label='Predicciones')
plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], color='red', linewidth=2, label='Línea de referencia')
plt.xlabel("Valores reales")
plt.ylabel("Predicciones")
plt.title("Modelo Inicial - Valores reales vs Predicciones")
plt.legend()
plt.grid(True)
plt.show()

# === 4. Optimización ===
param_grid = {
    'alpha': [0.01, 0.1, 1.0, 10.0, 100.0],
    'solver': ['auto', 'svd', 'cholesky', 'lsqr', 'sparse_cg']
}

grid_search = GridSearchCV(modelo, param_grid, cv=3, scoring='r2', n_jobs=-1)
grid_search.fit(X_train, y_train)

modelo_opt = grid_search.best_estimator_
y_pred_opt = modelo_opt.predict(X_test)
r2_opt = r2_score(y_test, y_pred_opt)

print("\n=== Optimización ===\n")
print(f"Mejores parámetros: {grid_search.best_params_}")
print(f"R² optimizado: {r2_opt:.4f}")
print(f"Mejora: {(r2_opt - r2_inicial) * 100:.2f}%")

# 📊 Gráfico de dispersión optimizado
plt.figure(figsize=(8, 6))
plt.scatter(y_test, y_pred_opt, color='green', label='Predicciones Optimizado')
plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], color='red', linewidth=2, label='Línea de referencia')
plt.xlabel("Valores reales")
plt.ylabel("Predicciones")
plt.title("Modelo Optimizado - Valores reales vs Predicciones")
plt.legend()
plt.grid(True)
plt.show()

# === 5. Segmentación (Clustering) ===
kmeans = KMeans(n_clusters=3, random_state=42)
df_grouped['cluster'] = kmeans.fit_predict(df_grouped[['edad', 'calificacion']])

# === 6. Perfiles de usuario ===
perfiles = df_grouped.groupby('cluster')[['edad', 'calificacion']].mean()

print("\n=== Perfiles de Usuario ===\n")
print(perfiles)

# 📊 Gráfico de Clustering
plt.figure(figsize=(8, 6))
for cluster_id in range(3):
    cluster_data = df_grouped[df_grouped['cluster'] == cluster_id]
    plt.scatter(cluster_data['edad'], cluster_data['calificacion'], label=f'Cluster {cluster_id}')

plt.xlabel('Edad')
plt.ylabel('Calificación Promedio')
plt.title('Clustering de Usuarios - KMeans')
plt.legend()
plt.grid(True)
plt.show()
