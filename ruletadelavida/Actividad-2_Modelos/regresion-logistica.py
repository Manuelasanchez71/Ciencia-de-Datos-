from sklearn.model_selection import train_test_split 
from sklearn.linear_model import LogisticRegression 
from sklearn.datasets import load_iris 
from sklearn.metrics import accuracy_score 
# Cargar un conjunto de datos (Iris en este caso) 
data = load_iris() 
X = data.data 
y = data.target 
# Convertimos a un problema binario (0: Setosa, 1: No Setosa) 
y = (y == 0).astype(int) 
# Dividir en entrenamiento y prueba 
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, 
random_state=42) 
# Crear y entrenar el modelo 
model = LogisticRegression() 
model.fit(X_train, y_train) 
# Realizar predicciones 
y_pred = model.predict(X_test) 
# Evaluar el modelo 
print(f"Precisión: {accuracy_score(y_test, y_pred)}") 