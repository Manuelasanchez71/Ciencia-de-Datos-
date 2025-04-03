from sklearn.neighbors import KNeighborsClassifier 
from sklearn.model_selection import train_test_split 
from sklearn.datasets import load_iris 
from sklearn.metrics import accuracy_score 
# Cargar el conjunto de datos Iris 
data = load_iris() 
X = data.data 
y = data.target 
# Dividir en entrenamiento y prueba 
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, 
random_state=42) 
# Crear el modelo KNN 
model = KNeighborsClassifier(n_neighbors=3) 
model.fit(X_train, y_train) 
# Realizar predicciones 
y_pred = model.predict(X_test) 
# Evaluar el modelo 
print(f"Precisión: {accuracy_score(y_test, y_pred)}")