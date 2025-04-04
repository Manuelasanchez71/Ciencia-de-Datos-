import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt 
import seaborn as sns 
from sklearn.model_selection import train_test_split 
from sklearn.linear_model import LinearRegression 
from sklearn.metrics import mean_squared_error, r2_score

#Cargar el conjunto de datos Iris desde seaborn 
data = sns.load_dataset('iris') 

#ver las primeras filas del conjunto de datos 
print(data.head()) 

#preparación de los datos 
# Seleccionamos las características (features) y la variable objetivo (target) 
X = data[['sepal_length', 'sepal_width', 'petal_width']] # Variables predictoras 
y = data['petal_length'] # Variable objetivo 

# Dividir el conjunto de datos en entrenamiento y prueba (80% entrenamiento, 20% prueba) 
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42) 

print("Tamaño del conjunto de entrenamiento:", X_train.shape) 
print("Tamaño del conjunto de prueba:", X_test.shape)

#Creación del modelo de regresión lineal  
# Crear el modelo de regresión lineal 
model = LinearRegression() 
# Entrenar el modelo 
model.fit(X_train, y_train) 
# Ver los coeficientes y la intersección (intercepto) del modelo 
print(f"Coeficientes: {model.coef_}") 
print(f"Intersección (intercepto): {model.intercept_}") 

#Hacer predicciones 
# Realizar predicciones sobre el conjunto de prueba 
y_pred = model.predict(X_test) 
# Mostrar las predicciones y los valores reales 
predictions_df = pd.DataFrame({'Real': y_test, 'Predicción': y_pred}) 

print(predictions_df.head()) 

#Evaluación del modelo 
# Calcular el error cuadrático medio (MSE) y R² 
mse = mean_squared_error(y_test, y_pred) 
r2 = r2_score(y_test, y_pred) 
print(f"Error cuadrático medio (MSE): {mse}") 
print(f"Coeficiente de determinación R²: {r2}")  

#Visualización de resultados 
# Graficar los valores reales vs. las predicciones 
plt.figure(figsize=(8, 6)) 
plt.scatter(y_test, y_pred, color='blue', label='Predicciones') 
plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 
color='red', linewidth=2, label="Línea de referencia") 
plt.xlabel("Valores reales") 
plt.ylabel("Predicciones") 
plt.title("Valores reales vs Predicciones") 
plt.legend() 
plt.show() 
