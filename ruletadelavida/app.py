from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for, session, flash
import sqlite3
import pandas as pd
import io
import os
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import matplotlib.pyplot as plt
import numpy as np
import base64
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_aqui'  # Cambia esto por una clave secreta real

def init_db():
    db_exists = os.path.exists("database.db")
    with sqlite3.connect("database.db") as conn:
        cursor = conn.cursor()
        if not db_exists:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS usuarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    role TEXT NOT NULL
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS respuestas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    usuario_id INTEGER,
                    nombre TEXT,
                    edad INTEGER,
                    sexo TEXT,
                    estado_civil TEXT,
                    categoria TEXT,
                    pregunta TEXT,
                    calificacion INTEGER,
                    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
                )
            ''')
            # Crear un usuario administrador por defecto solo si la base de datos es nueva
            cursor.execute("INSERT OR IGNORE INTO usuarios (username, password, role) VALUES (?, ?, ?)",
                           ('admin', generate_password_hash('admin123'), 'admin'))
        conn.commit()

init_db()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session or session.get('role') != 'admin':
            flash('Acceso no autorizado')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
@login_required
def index():
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
                session['user_id'] = user[0]
                session['role'] = user[3]
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
                cursor.execute("INSERT INTO usuarios (username, password, role) VALUES (?, ?, ?)", 
                               (username, hashed_password, 'user'))  # Asignamos el rol 'user' por defecto
                conn.commit()
            flash('Registro exitoso. Por favor, inicia sesión.')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('El nombre de usuario ya existe. Por favor, elige otro.')
    
    return render_template('registro.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/guardar', methods=['POST'])
@login_required
def guardar():
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
                        INSERT INTO respuestas (usuario_id, nombre, edad, sexo, estado_civil, categoria, pregunta, calificacion)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (session['user_id'], data['nombre'], data['edad'], data['sexo'], data['estado_civil'], 
                          categoria, pregunta, data[f"{categoria}_{i+1}"]))
            
            conn.commit()

        return jsonify({"mensaje": "Respuestas guardadas exitosamente."})

    except Exception as e:
        return jsonify({"error": f"Error interno: {str(e)}"}), 500

@app.route('/mis_respuestas')
@login_required
def mis_respuestas():
    with sqlite3.connect("database.db") as conn:
        df = pd.read_sql_query("SELECT * FROM respuestas WHERE usuario_id = ?", conn, params=(session['user_id'],))
    
    # Procesar los datos para mostrarlos en la plantilla
    respuestas_por_categoria = df.groupby('categoria')['calificacion'].mean().to_dict()
    
    # Generar el gráfico
    grafico_base64 = generar_grafico(session['user_id'])
    
    return render_template('mis_respuestas.html', respuestas=respuestas_por_categoria, grafico=grafico_base64)

def generar_grafico(user_id):
    try:
        with sqlite3.connect("database.db") as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT categoria, AVG(calificacion)
                FROM respuestas
                WHERE usuario_id = ?
                GROUP BY categoria
            ''', (user_id,))
            datos = cursor.fetchall()

        if not datos:
            return None

        categorias = [fila[0] for fila in datos]
        valores = [fila[1] for fila in datos]

        valores.append(valores[0])

        N = len(categorias)
        angulos = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
        angulos += angulos[:1]

        fig, ax = plt.subplots(figsize=(7, 7), subplot_kw=dict(polar=True))

        ax.fill(angulos, valores, color='b', alpha=0.3)
        ax.plot(angulos, valores, color='b', linewidth=2)

        ax.set_xticks(angulos[:-1])
        ax.set_xticklabels(categorias, fontsize=10)
        ax.set_yticks(range(1, 11))
        ax.set_ylim(1, 10)
        ax.yaxis.grid(True)

        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', bbox_inches='tight')
        img_buffer.seek(0)
        plt.close()

        img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
        return img_base64

    except Exception as e:
        print(f"Error al generar el gráfico: {str(e)}")
        return None

@app.route('/admin/usuarios')
@admin_required
def admin_usuarios():
    with sqlite3.connect("database.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, username FROM usuarios WHERE role = 'user'")
        usuarios = cursor.fetchall()
    return render_template('admin_usuarios.html', usuarios=usuarios)

@app.route('/admin/usuario/<int:user_id>')
@admin_required
def admin_ver_usuario(user_id):
    with sqlite3.connect("database.db") as conn:
        df = pd.read_sql_query("SELECT * FROM respuestas WHERE usuario_id = ?", conn, params=(user_id,))
    
    if df.empty:
        flash('Este usuario aún no ha respondido la encuesta.')
        return redirect(url_for('admin_usuarios'))
    
    respuestas_por_categoria = df.groupby('categoria')['calificacion'].mean().to_dict()
    grafico_base64 = generar_grafico(user_id)
    
    return render_template('admin_ver_usuario.html', 
                           respuestas=respuestas_por_categoria, 
                           grafico=grafico_base64, 
                           user_id=user_id)

@app.route('/admin')
@admin_required
def admin_dashboard():
    with sqlite3.connect("database.db") as conn:
        df = pd.read_sql_query("SELECT * FROM respuestas", conn)
    
    # Si no hay datos, mostrar valores predeterminados
    if df.empty:
        return render_template('admin_dashboard.html', 
                           total_usuarios=0,
                           promedio_general=0,
                           categorias=[],
                           promedios=[],
                           distribucion_labels=[],
                           distribucion_values=[],
                           progreso_fechas=[],
                           progreso_valores=[])
    
    # Análisis general
    total_usuarios = df['usuario_id'].nunique()
    promedio_general = df['calificacion'].mean()
    
    # Promedios por categoría
    promedios_por_categoria = df.groupby('categoria')['calificacion'].mean().to_dict()
    categorias = list(promedios_por_categoria.keys())
    promedios = list(promedios_por_categoria.values())
    
    # Distribución general
    distribucion = df['categoria'].value_counts().sort_index().to_dict()
    distribucion_labels = [str(k) for k in distribucion.keys()]
    distribucion_values = list(distribucion.values())
    
    # Progreso en el tiempo
    df['fecha'] = pd.to_datetime(df['fecha'])
    progreso_tiempo = df.groupby(df['fecha'].dt.date)['calificacion'].mean().reset_index()
    progreso_tiempo = progreso_tiempo.sort_values('fecha')
    
    progreso_fechas = [fecha.strftime('%Y-%m-%d') for fecha in progreso_tiempo['fecha']]
    progreso_valores = list(progreso_tiempo['calificacion'])
    
    return render_template('admin_dashboard.html', 
                           total_usuarios=total_usuarios,
                           promedio_general=promedio_general,
                           categorias=categorias,
                           promedios=promedios,
                           distribucion_labels=distribucion_labels,
                           distribucion_values=distribucion_values,
                           progreso_fechas=progreso_fechas,
                           progreso_valores=progreso_valores)

@app.route('/admin/filtrar_datos', methods=['POST'])
@admin_required
def filtrar_datos():
    categoria = request.form.get('categoria')
    
    with sqlite3.connect("database.db") as conn:
        if categoria == 'todas':
            df = pd.read_sql_query("SELECT * FROM respuestas", conn)
        else:
            df = pd.read_sql_query("SELECT * FROM respuestas WHERE categoria = ?", conn, params=(categoria,))
    
    # Si no hay datos, devolver valores predeterminados
    if df.empty:
        return jsonify({
            'promedio_general': 0,
            'distribucion_labels': [],
            'distribucion_values': [],
            'progreso_fechas': [],
            'progreso_valores': []
        })
    
    promedio_general = df['calificacion'].mean()
    # Distribución por categoría o por pregunta
    if categoria == 'todas':
        distribucion = df.groupby('categoria').size().to_dict()
    else:
        # Si se filtra por una categoría específica, mostrar distribución por pregunta
        distribucion = df[df['categoria'] == categoria].groupby('pregunta').size().to_dict()
    
    distribucion_labels = list(distribucion.keys())
    distribucion_values = list(distribucion.values())
    
    df['fecha'] = pd.to_datetime(df['fecha'])
    progreso_tiempo = df.groupby(df['fecha'].dt.date)['calificacion'].mean().reset_index()
    progreso_tiempo = progreso_tiempo.sort_values('fecha')
    
    return jsonify({
        'promedio_general': round(promedio_general, 2) if not pd.isna(promedio_general) else 0,
        'distribucion_labels': distribucion_labels,
        'distribucion_values': distribucion_values,
        'progreso_fechas': [fecha.strftime('%Y-%m-%d') for fecha in progreso_tiempo['fecha']],
        'progreso_valores': list(progreso_tiempo['calificacion'])
    })

@app.route('/descargar_excel')
@admin_required
def descargar_excel():
    try:
        with sqlite3.connect("database.db") as conn:
            df = pd.read_sql_query("""
                SELECT r.*, u.username 
                FROM respuestas r
                JOIN usuarios u ON r.usuario_id = u.id
            """, conn)
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Todas las Respuestas', index=False)
            
            # Crear una hoja de resumen
            resumen = pd.DataFrame({
                'Total Usuarios': [df['usuario_id'].nunique()],
                'Promedio General': [df['calificacion'].mean()],
            })
            
            # Calcular promedios por categoría
            promedios_por_categoria = df.groupby('categoria')['calificacion'].mean().reset_index()
            promedios_por_categoria.columns = ['Categoría', 'Promedio']
            
            # Combinar resumen y promedios por categoría
            resumen = pd.concat([resumen, promedios_por_categoria], ignore_index=True)
            resumen.to_excel(writer, sheet_name='Resumen', index=False)
        
        output.seek(0)
        return send_file(output, 
                         download_name='respuestas_ruleta_vida.xlsx',
                         as_attachment=True,
                         mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    except Exception as e:
        return jsonify({"error": f"Error al generar Excel: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True)

