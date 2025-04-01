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
     # 🔹 Elimina el usuario si existe antes de probar
    with sqlite3.connect("database.db") as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM usuarios WHERE username = 'usuario_test'")
        conn.commit()
        
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
    # Hacer login para crear sesión
    response = client.post('/login', data={
        'username': 'usuario_prueba',
        'password': '123456'
    }, follow_redirects=True)
    assert response.status_code == 200

    # Datos de encuesta completa
    data = {
        'nombre': 'Jaqueline',
        'edad': 31,
        'sexo': 'Femenino',
        'estado_civil': 'Soltero'
    }
    data.update({f'salud_y_bienestar_{i}': 5 for i in range(1, 4)})
    data.update({f'relaciones_{i}': 4 for i in range(1, 3)})
    data.update({f'carrera_y_proposito_{i}': 3 for i in range(1, 4)})
    data.update({f'finanzas_{i}': 4 for i in range(1, 4)})
    data.update({f'desarrollo_personal_y_crecimiento_{i}': 5 for i in range(1, 4)})
    data.update({f'diversion_y_ocio_{i}': 4 for i in range(1, 4)})
    data.update({f'espiritualidad_{i}': 5 for i in range(1, 4)})
    data.update({f'entorno_fisico_y_hogar_{i}': 3 for i in range(1, 4)})

    # Enviar encuesta
    response = client.post('/guardar', json=data, follow_redirects=True)
    assert response.status_code == 200
    json_response = response.get_json()
    assert json_response['mensaje'] == "Respuestas guardadas exitosamente."

# P05 - Enviar encuesta incompleta
def test_encuesta_incompleta(client, setup_usuario):
    # Login antes de enviar
    response = client.post('/login', data={
        'username': 'usuario_prueba',
        'password': '123456'
    }, follow_redirects=True)
    assert response.status_code == 200

    # Datos incompletos (faltan las respuestas)
    data = {'nombre': 'Jaqueline', 'edad': 31}
    response = client.post('/guardar', json=data, follow_redirects=True)
    assert response.status_code == 500
    json_response = response.get_json()
    assert "error" in json_response
    assert "Error interno" in json_response["error"]

# P07 - Visualizar "Mis Respuestas"
def test_mis_respuestas(client, setup_usuario):
    # Insertar respuestas de prueba
    with sqlite3.connect("database.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO respuestas (usuario_id, nombre, edad, sexo, estado_civil, categoria, pregunta, calificacion)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (2, "usuario_prueba", 30, "Femenino", "Soltero", "salud_y_bienestar",
              "¿Cómo te sientes físicamente en general?", 8))
        conn.commit()

    # Hacer login
    response = client.post('/login', data={
        'username': 'usuario_prueba',
        'password': '123456'
    }, follow_redirects=True)
    assert response.status_code == 200

    # Obtener la página de Mis Respuestas
    response = client.get('/mis_respuestas', follow_redirects=True)
    assert response.status_code == 200
    response_text = response.data.decode('utf-8')

    # Comprobar que contiene la categoría o título
    assert "salud_y_bienestar" in response_text or "Resumen" in response_text


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
def test_dashboard(client, setup_usuario):
    # Primero, actualiza el usuario de prueba para que sea admin
    with sqlite3.connect("database.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE usuarios SET role = 'admin' WHERE id = 2
        """)
        conn.commit()

    # Iniciar sesión real (para que la sesión sea válida y fresh)
    response = client.post('/login', data={
        'username': 'usuario_prueba',
        'password': '123456'
    }, follow_redirects=True)
    assert response.status_code == 200

    # Acceder al dashboard
    response = client.get('/admin', follow_redirects=True)
    assert response.status_code == 200

    response_text = response.data.decode('utf-8')
    assert "Dashboard" in response_text or "Estadísticas" in response_text, "❌ No se encontró 'Dashboard' en la página."

# P11 - Ver lista de usuarios
def test_ver_usuarios(client, setup_usuario):
    # 🔹 Actualiza el usuario de prueba como admin
    with sqlite3.connect("database.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE usuarios SET role = 'admin' WHERE id = 2
        """)
        conn.commit()

    # 🔹 Inicia sesión real
    response = client.post('/login', data={
        'username': 'usuario_prueba',
        'password': '123456'
    }, follow_redirects=True)
    assert response.status_code == 200

    # 🔹 Solicita la lista de usuarios
    response = client.get('/admin/usuarios', follow_redirects=True)
    assert response.status_code == 200

    response_text = response.data.decode('utf-8')
    assert "Lista de Usuarios" in response_text or "Usuarios" in response_text, "❌ No apareció la lista de usuarios."

# P12 - Ver respuestas del usuario
def test_ver_respuestas_usuario(client):
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['role'] = 'admin'
    response = client.get('/admin/usuario/2', follow_redirects=True)
    assert response.status_code == 200

# P13 - Editar usuario
def test_editar_usuario(client, setup_usuario):
    # 🔹 Asignar rol admin al usuario de prueba
    with sqlite3.connect("database.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE usuarios SET role = 'admin' WHERE id = 2
        """)
        conn.commit()

    # 🔹 Login como admin
    response = client.post('/login', data={
        'username': 'usuario_prueba',
        'password': '123456'
    }, follow_redirects=True)
    assert response.status_code == 200

    # 🔹 Actualizar datos del usuario
    response = client.post('/admin/actualizar_usuario/2', data={
        'username': 'usuario_actualizado',
        'role': 'usuario',
        'password': ''
    }, follow_redirects=True)
    assert response.status_code == 200
    response_text = response.data.decode('utf-8')
    assert "Usuario actualizado correctamente" in response_text, "❌ El mensaje de actualización no apareció."

# P14 - Eliminar usuario
def test_eliminar_usuario(client, setup_usuario):
    # 🔹 Crear usuario a eliminar con id 3
    with sqlite3.connect("database.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO usuarios (id, username, password, email, phone, role)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO NOTHING
        """, (3, 'usuario_eliminar', '123456', 'correo3@example.com', '0000000000', 'usuario'))
        conn.commit()

    # 🔹 Cambiar rol de usuario de prueba a admin
    with sqlite3.connect("database.db") as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE usuarios SET role = 'admin' WHERE id = 2")
        conn.commit()

    # 🔹 Login como admin (usuario_prueba)
    response = client.post('/login', data={
        'username': 'usuario_prueba',
        'password': '123456'
    }, follow_redirects=True)
    assert response.status_code == 200

    # 🔹 Eliminar usuario
    response = client.post('/admin/eliminar_usuario/3', follow_redirects=True)
    assert response.status_code == 200
    response_text = response.data.decode('utf-8')
    assert "Usuario y sus respuestas eliminados correctamente" in response_text

    # ✅ Verificar que no exista
    with sqlite3.connect("database.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM usuarios WHERE id = 3")
        usuario = cursor.fetchone()
        assert usuario is None, "❌ El usuario no fue eliminado de la base de datos."

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
def test_descargar_excel(client, setup_usuario):
    # 🔹 Asignar rol admin al usuario de prueba
    with sqlite3.connect("database.db") as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE usuarios SET role = 'admin' WHERE id = 2")
        conn.commit()

    # 🔹 Login como admin
    response = client.post('/login', data={
        'username': 'usuario_prueba',
        'password': '123456'
    }, follow_redirects=True)
    assert response.status_code == 200

    # 🔹 Descargar Excel
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