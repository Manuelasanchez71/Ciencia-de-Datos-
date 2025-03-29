import pytest
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

@pytest.fixture
def setup_usuario():
    """Crea un usuario de prueba en la base de datos antes de ejecutar la prueba."""
    hashed_password = generate_password_hash("123456")

    with sqlite3.connect("database.db") as conn:
        cursor = conn.cursor()

        # 🔹 Inserta o actualiza el usuario con contraseña encriptada
        cursor.execute("""
            INSERT INTO usuarios (id, username, password, email, phone, role)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET 
                username=excluded.username, 
                password=excluded.password, 
                email=excluded.email, 
                phone=excluded.phone, 
                role=excluded.role
        """, (2, 'usuario_prueba', hashed_password, 'correo@example.com', '9876543210', 'user'))     
        conn.commit()

        # 🔍 Verifica si el usuario realmente se insertó
        cursor.execute("SELECT id, username, password, role FROM usuarios WHERE id = 2")
        usuario = cursor.fetchone()
        assert usuario is not None, "❌ No se pudo crear el usuario en la BD."

        print("✅ Usuario creado:", usuario)

        # 🔹 Verifica si la contraseña almacenada coincide con la ingresada
        assert check_password_hash(usuario[2], "123456"), "❌ El hash de la contraseña no coincide."

    yield usuario  # Devuelve el usuario para su uso en las pruebas

    # 🔄 Elimina el usuario después de la prueba
    with sqlite3.connect("database.db") as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM usuarios WHERE id = ?", (2,))
        conn.commit()
        print("❌ Usuario eliminado después de la prueba")
