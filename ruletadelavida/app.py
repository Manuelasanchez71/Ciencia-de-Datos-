from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for, session, flash
import sqlite3
import pandas as pd
import io
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'ruletadelavida'  # Cambia esto por una clave secreta real


if os.path.exists("database.db"):
    os.remove("database.db")


def init_db():
    with sqlite3.connect("database.db") as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS respuestas (
                nombre TEXT,
                edad INTEGER,
                sexo TEXT,
                estado_civil TEXT,
                categoria TEXT,
                pregunta TEXT,
                calificacion INTEGER
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        conn.commit()

init_db()

@app.route('/')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template("index.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        with sqlite3.connect("database.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM usuarios WHERE username = ?", (username,))
            user = cursor.fetchone()
            
            if user and check_password_hash(user[2], password):
                session['username'] = username
                return redirect(url_for('index'))
            else:
                flash('Usuario o contraseña incorrectos')
    
    return render_template('login.html')

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password)
        
        try:
            with sqlite3.connect("database.db") as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO usuarios (username, password) VALUES (?, ?)", (username, hashed_password))
                conn.commit()
            flash('Registro exitoso. Por favor, inicia sesión.')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('El nombre de usuario ya existe. Por favor, elige otro.')
    
    return render_template('registro.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/guardar', methods=['POST'])
def guardar():

    if 'username' not in session:
        return jsonify({"error": "No autorizado"}), 401

    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No se recibieron datos"}), 400

        with sqlite3.connect("database.db") as conn:
            cursor = conn.cursor()
            
            categorias = {
                "salud_y_bienestar": ["¿Cómo te sientes físicamente en general?", 
                                      "¿Estás tomando decisiones saludables con respecto a tu alimentación y ejercicio?",
                                      "¿Estás durmiendo lo suficiente para sentirte descansado?"],
                "relaciones": ["¿Cómo es tu relación con tu familia, amigos y pareja?",
                               "¿Estás comunicándote de manera efectiva con las personas importantes en tu vida?"],
                "carrera_y_proposito":["¿Sientes que estás progresando en tu carrera?",
                                       "¿Tienes claro tu propósito o lo que te gustaría lograr en tu vida profesional?", 
                                       "¿Estás buscando oportunidades para crecer profesionalmente?"], 
                "finanzas": ["¿Te sientes seguro/a financieramente?", 
                             "¿Estás gestionando tu dinero de manera efectiva (ahorros, inversiones, gastos)?", 
                             "¿Tienes un plan financiero a corto y largo plazo?"], 
                "desarrollo_personal_y_crecimiento": ["¿Te sientes motivado/a para mejorar y crecer como persona?", 
                                                      "¿Estás tomando tiempo para reflexionar y trabajar en tu autoconocimiento?", 
                                                      "¿Tienes metas claras de desarrollo personal?"], 
                "diversion_y_ocio": ["¿Estás dedicando tiempo a actividades que disfrutas?", 
                                     "¿Tienes hobbies o intereses que te ayudan a desconectar?", 
                                     "¿Te sientes equilibrado/a entre el estudio y el tiempo libre?"], 
                "espiritualidad": ["¿Sientes que tienes un propósito más grande en la vida?", 
                                   "¿Te sientes en paz con tu vida y tus creencias?", 
                                   "¿Estás tomando tiempo para reflexionar sobre tu vida y tu conexión con el mundo?"], 
                "entorno_fisico_y_hogar": ["¿Te sientes cómodo/a y organizado/a en tu espacio de vida?", 
                                           "¿Tu entorno te inspira o te ayuda a relajarte y ser productivo/a?", 
                                           "¿Tienes un lugar que te permita desconectar y recargar energías?"]
            }
            
            for categoria, preguntas in categorias.items():
                for i, pregunta in enumerate(preguntas):
                    cursor.execute('''
                        INSERT INTO respuestas (nombre, edad, sexo, estado_civil, categoria, pregunta, calificacion)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (data['nombre'], data['edad'], data['sexo'], data['estado_civil'], 
                          categoria, pregunta, data[f"{categoria}_{i+1}"]))
            
            conn.commit()

        return jsonify({"mensaje": "Respuestas guardadas exitosamente."})

    except Exception as e:
        return jsonify({"error": f"Error interno: {str(e)}"}), 500

@app.route('/descargar_excel')
def descargar_excel():
    try:
        with sqlite3.connect("database.db") as conn:
            df = pd.read_sql_query("SELECT * FROM respuestas", conn)
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Respuestas', index=False)
        
        output.seek(0)
        return send_file(output, 
                         download_name='respuestas.xlsx',
                         as_attachment=True,
                         mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    except Exception as e:
        return jsonify({"error": f"Error al generar Excel: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True)