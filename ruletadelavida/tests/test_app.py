import pytest
import re
import sqlite3
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

# P01 - Registro exitoso
def test_registro_exitoso(client):
    response = client.post('/registro', data={
        'username': 'usuario_test',
        'password': '123456',
        'email': 'usuario_test@example.com',
        'phone': '1234567890'
    }, follow_redirects=True)
    assert response.status_code == 200
    response_text = response.data.decode('utf-8')
    assert "Iniciar Sesión" in response_text  


# P02 - Registro incompleto
def test_registro_incompleto(client):
    response = client.post('/registro', data={
        'username': '',
        'password': '123456',
        'email': 'correo@example.com',
        'phone': '9876543210'
    }, follow_redirects=True)

    assert response.status_code == 200
    response_text = response.data.decode('utf-8')

    # 🔴 DEBUG: Imprimir respuesta completa para ver qué está devolviendo Flask
    print("DEBUG RESPONSE:\n", response_text)

    assert "Todos los campos son obligatorios" in response_text



# P03 - Inicio de sesión correcto
def test_login_correcto(client, setup_usuario):
    response = client.post('/login', data={
        'username': 'usuario_prueba',
        'password': '123456'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    response_text = response.data.decode('utf-8')
    assert "Bienvenido" in response_text or "Inicio" in response_text


# P04 - Inicio de sesión fallido
def test_login_fallido(client):
    response = client.post('/login', data={
        'username': 'usuario_invalido',
        'password': '123456'
    }, follow_redirects=True)
    assert response.status_code == 200
    response_text = response.data.decode('utf-8')
    assert "Usuario o contraseña incorrectos" in response_text


# P05 - Enviar encuesta completa
def test_encuesta_completa(client, setup_usuario):
    with sqlite3.connect("database.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE id = 2")
        usuario = cursor.fetchone()
        assert usuario is not None, "❌ El usuario de prueba no se encontró en la base de datos."

    data = {f'salud_y_bienestar_{i}': 5 for i in range(1, 4)}
    # (sigue con el resto de los datos...)
    response = client.post('/guardar', json=data, follow_redirects=True)

    assert response.status_code == 200
    response_text = response.data.decode('utf-8')
    assert "Mis Respuestas" in response_text, "❌ La página no mostró 'Mis Respuestas', posible problema de autenticación."


# P06 - Enviar encuesta incompleta
def test_encuesta_incompleta(client):
    data = {'nombre': 'Usuario Test', 'edad': 25}
    with client.session_transaction() as sess:
        sess['user_id'] = 2
    response = client.post('/guardar', data=data, follow_redirects=True)
    assert response.status_code == 200
    response_text = response.data.decode('utf-8')
    assert "Faltan respuestas" in response_text


# P07 - Visualizar "Mis Respuestas"
def test_mis_respuestas(client):
    with client.session_transaction() as sess:
        sess['user_id'] = 2
    response = client.get('/mis_respuestas', follow_redirects=True)
    assert response.status_code == 200
    response_text = response.data.decode('utf-8')
    assert "Resumen" in response_text

# P08 - Enviar mensaje de contacto
def test_contacto_exitoso(client):
    response = client.post('/enviar_contacto', data={
        'nombre': 'Manuela',
        'email': 'manuela@example.com',
        'mensaje': 'Mensaje de prueba'
    }, follow_redirects=True)
    assert response.status_code == 200
    response_text = response.data.decode('utf-8')
    assert "Mensaje enviado" in response_text

# P09 - Enviar mensaje contacto incompleto
def test_contacto_incompleto(client):
    response = client.post('/enviar_contacto', data={
        'nombre': '',
        'email': '',
        'mensaje': ''
    }, follow_redirects=True)
    assert response.status_code == 200
    response_text = response.data.decode('utf-8')
    assert "Por favor, completa todos los campos" in response_text

# P10 - Acceso al dashboard
def test_dashboard(client):
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['role'] = 'admin'
        sess['_fresh'] = True  # Asegura que la sesión es válida
        print("🔍 Sesión antes de GET:", dict(sess))

    response = client.get('/admin', follow_redirects=True)
    
    # 🔹 Verifica qué devuelve la respuesta
    print("🔍 Respuesta después de GET:", response.data.decode('utf-8'))

    assert response.status_code == 200
    response_text = response.data.decode('utf-8')
    assert "Dashboard" in response_text, "❌ No se encontró 'Dashboard', posible problema de autenticación."


# P11 - Ver lista de usuarios
def test_ver_usuarios(client):
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['role'] = 'admin'
    response = client.get('/admin/usuarios', follow_redirects=True)
    assert response.status_code == 200
    response_text = response.data.decode('utf-8')
    assert "Lista de Usuarios" in response_text

# P12 - Ver respuestas del usuario
def test_ver_respuestas_usuario(client):
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['role'] = 'admin'
    response = client.get('/admin/usuario/2', follow_redirects=True)
    assert response.status_code == 200

# P13 - Editar usuario
def test_editar_usuario(client):
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['role'] = 'admin'
    response = client.post('/admin/actualizar_usuario/2', data={
        'username': 'usuario_actualizado',
        'role': 'usuario',
        'password': ''
    }, follow_redirects=True)
    assert response.status_code == 200
    response_text = response.data.decode('utf-8')
    assert "Usuario actualizado" in response_text

# P14 - Eliminar usuario
def test_eliminar_usuario(client):
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['role'] = 'admin'
    response = client.post('/admin/eliminar_usuario/3', follow_redirects=True)
    assert response.status_code == 200
    response_text = response.data.decode('utf-8')
    assert "Usuario y sus respuestas eliminados" in response_text

# P15 - Aplicar filtros en análisis
def test_aplicar_filtros(client):
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['role'] = 'admin'
    response = client.post('/admin/filtrar_analisis', data={
        'categoria': 'Salud',
        'edad': '26-35',
        'sexo': 'Femenino'
    }, follow_redirects=True)
    assert response.status_code == 200

# P16 - Descargar Excel
def test_descargar_excel(client):
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['role'] = 'admin'
    response = client.get('/descargar_excel', follow_redirects=True)
    assert response.status_code == 200
    assert response.mimetype == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

# P17 - Visualizar mensajes de contacto
def test_ver_contactos(client):
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['role'] = 'admin'
    response = client.get('/admin/contactos', follow_redirects=True)
    assert response.status_code == 200
    response_text = response.data.decode('utf-8')
    assert "Mensajes de Contacto" in response_text

# P18 - Visualizar página Nosotros
def test_nosotros(client):
    response = client.get('/nosotros')
    assert response.status_code == 200
    response_text = response.data.decode('utf-8')
    assert "Sobre Nosotros" in response_text