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
app.secret_key = 'ruletadelavida'  #clave secreta real

# if os.path.exists("database.db"):
#     os.remove("database.db")

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
                    email TEXT NOT NULL, 
                    phone TEXT NOT NULL, 
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
            cursor.execute("INSERT OR IGNORE INTO usuarios (username, password, email, phone, role) VALUES (?, ?, ?, ?, ?)",
                           ('admin', generate_password_hash('admin123'), 'admin@example.com', '1234567890', 'admin'))
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
                session['role'] = user[5]
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
        email = request.form['email']
        phone = request.form['phone']
        
        try:
            with sqlite3.connect("database.db") as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO usuarios (username, password, email, phone, role) VALUES (?, ?, ?, ?, ?)", 
                               (username, hashed_password, email, phone, 'user'))  # Asignamos el rol 'user' por defecto
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
        cursor.execute("SELECT id, username, role FROM usuarios")
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


@app.route('/admin/editar_usuario/<int:user_id>')
@admin_required
def admin_editar_usuario(user_id):
    with sqlite3.connect("database.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, role FROM usuarios WHERE id = ?", (user_id,))
        usuario = cursor.fetchone()
        
        if not usuario:
            flash("Usuario no encontrado", "error")
            return redirect(url_for('admin_usuarios'))
        
        # Si el rol no está en la base de datos, asignar 'usuario' por defecto
        if len(usuario) < 3:
            usuario = list(usuario)
            usuario.append('usuario')
            
    return render_template('admin_editar_usuario.html', usuario=usuario)

@app.route('/admin/actualizar_usuario/<int:user_id>', methods=['POST'])
@admin_required
def admin_actualizar_usuario(user_id):
    username = request.form.get('username')
    role = request.form.get('role')
    password = request.form.get('password')
    
    if not username:
        flash("El nombre de usuario es obligatorio", "error")
        return redirect(url_for('admin_editar_usuario', user_id=user_id))
    
    with sqlite3.connect("database.db") as conn:
        cursor = conn.cursor()
        
        # Verificar si el nombre de usuario ya existe (excepto para el usuario actual)
        cursor.execute("SELECT id FROM usuarios WHERE username = ? AND id != ?", (username, user_id))
        if cursor.fetchone():
            flash("El nombre de usuario ya está en uso", "error")
            return redirect(url_for('admin_editar_usuario', user_id=user_id))
        
        # Actualizar el usuario
        if password:
            # Si se proporciona una nueva contraseña, actualizarla también
            hashed_password = generate_password_hash(password)
            cursor.execute("UPDATE usuarios SET username = ?, password = ?, role = ? WHERE id = ?", 
                          (username, hashed_password, role, user_id))
        else:
            # Si no se proporciona contraseña, mantener la actual
            cursor.execute("UPDATE usuarios SET username = ?, role = ? WHERE id = ?", 
                          (username, role, user_id))
        
        conn.commit()
        
    flash("Usuario actualizado correctamente")
    return redirect(url_for('admin_usuarios'))

@app.route('/admin/eliminar_usuario/<int:user_id>', methods=['POST'])
@admin_required
def admin_eliminar_usuario(user_id):
    with sqlite3.connect("database.db") as conn:
        cursor = conn.cursor()
        
        # Verificar que no estamos eliminando al usuario actual
        if session.get('user_id') == user_id:
            flash("No puedes eliminar tu propio usuario", "error")
            return redirect(url_for('admin_usuarios'))
        
        # Eliminar las respuestas asociadas al usuario
        cursor.execute("DELETE FROM respuestas WHERE usuario_id = ?", (user_id,))
        
        # Eliminar el usuario
        cursor.execute("DELETE FROM usuarios WHERE id = ?", (user_id,))
        conn.commit()
        
    flash("Usuario y sus respuestas eliminados correctamente")
    return redirect(url_for('admin_usuarios'))

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

    
@app.route('/admin/analisis')
@admin_required
def admin_analisis():
    with sqlite3.connect("database.db") as conn:
        df = pd.read_sql_query("SELECT * FROM respuestas", conn)
    
    # Si no hay datos, mostrar valores predeterminados
    if df.empty:
        return render_template('admin_analisis.html', 
                         categorias=[],
                         grupos_edad=[],
                         sexos=[],
                         promedio_general=0,
                         desviacion_estandar=0,
                         total_respuestas=0,
                         usuarios_unicos=0,
                         top_categorias=[],
                         bottom_categorias=[],
                         diferencias_demograficas=[],
                         correlaciones_importantes=[],
                         datos_calificaciones={"labels": [], "data": []},
                         datos_categorias={"labels": [], "data": []},
                         datos_edad={"labels": [], "data": []},
                         datos_sexo={"labels": [], "data": []},
                         datos_radar={"labels": [], "data": []},
                         datos_tendencia={"labels": [], "data": []},
                         datos_correlacion={"labels": [], "datasets": []})
    
    # Preparar datos para la plantilla
    # 1. Estadísticas generales
    promedio_general = float(df['calificacion'].mean())
    desviacion_estandar = float(df['calificacion'].std())
    total_respuestas = len(df)
    usuarios_unicos = df['usuario_id'].nunique()
    
    # 2. Listas para filtros
    categorias = sorted(df['categoria'].unique())
    
    # Crear grupos de edad - Asegurarse de que la columna 'edad' sea numérica
    df['edad'] = pd.to_numeric(df['edad'], errors='coerce')
    
    # Crear grupos de edad solo para filas con edad válida
    df_con_edad = df.dropna(subset=['edad'])
    df_con_edad['grupo_edad'] = pd.cut(
        df_con_edad['edad'], 
        bins=[0, 25, 35, 45, 55, 100], 
        labels=['18-25', '26-35', '36-45', '46-55', '56+'], 
        right=False
    )
    
    # Obtener grupos de edad únicos
    grupos_edad = sorted(df_con_edad['grupo_edad'].astype(str).unique())
    
    sexos = sorted(df['sexo'].unique())
    
    # 3. Top y bottom categorías
    cat_avg = df.groupby('categoria')['calificacion'].mean()
    top_categorias = [{"nombre": cat, "valor": float(val)} for cat, val in cat_avg.nlargest(3).items()]
    bottom_categorias = [{"nombre": cat, "valor": float(val)} for cat, val in cat_avg.nsmallest(3).items()]
    
    # 4. Diferencias demográficas
    diferencias_demograficas = []
    
    # Por sexo
    sexo_diff = df.groupby('sexo')['calificacion'].mean().max() - df.groupby('sexo')['calificacion'].mean().min()
    if sexo_diff > 0.5:  # Umbral arbitrario para considerar una diferencia significativa
        sexo_max = df.groupby('sexo')['calificacion'].mean().idxmax()
        sexo_min = df.groupby('sexo')['calificacion'].mean().idxmin()
        diferencias_demograficas.append(f"Diferencia por sexo: {sexo_diff:.2f} puntos ({sexo_max} > {sexo_min})")
    
    # Por estado civil
    estado_diff = df.groupby('estado_civil')['calificacion'].mean().max() - df.groupby('estado_civil')['calificacion'].mean().min()
    if estado_diff > 0.5:
        estado_max = df.groupby('estado_civil')['calificacion'].mean().idxmax()
        estado_min = df.groupby('estado_civil')['calificacion'].mean().idxmin()
        diferencias_demograficas.append(f"Diferencia por estado civil: {estado_diff:.2f} puntos ({estado_max} > {estado_min})")
    
    # Por grupo de edad - Solo usar filas con grupo_edad válido
    if len(grupos_edad) > 1:
        edad_avg = df_con_edad.groupby('grupo_edad', observed=False)['calificacion'].mean()
        if not edad_avg.empty:
            edad_diff = edad_avg.max() - edad_avg.min()
            if edad_diff > 0.5:
                edad_max = edad_avg.idxmax()
                edad_min = edad_avg.idxmin()
                diferencias_demograficas.append(f"Diferencia por grupo de edad: {edad_diff:.2f} puntos ({edad_max} > {edad_min})")
    
    # 5. Correlaciones importantes
    # Crear un DataFrame con promedios por usuario y categoría
    user_cat_avg = df.groupby(['usuario_id', 'categoria'])['calificacion'].mean().unstack()
    
    # Calcular matriz de correlación entre categorías
    correlaciones_importantes = []
    if not user_cat_avg.empty and user_cat_avg.shape[1] > 1:
        cat_corr = user_cat_avg.corr()
        
        # Filtrar correlaciones fuertes (positivas o negativas)
        for i in range(len(cat_corr.columns)):
            for j in range(i+1, len(cat_corr.columns)):
                corr_val = cat_corr.iloc[i, j]
                if not pd.isna(corr_val) and abs(corr_val) > 0.6:  # Umbral arbitrario para correlación fuerte
                    tipo = "positiva" if corr_val > 0 else "negativa"
                    correlaciones_importantes.append(f"Correlación {tipo} entre {cat_corr.columns[i]} y {cat_corr.columns[j]}: {corr_val:.2f}")
    
    # 6. Datos para gráficos
    # Distribución de calificaciones
    calificaciones_counts = df['calificacion'].value_counts().sort_index()
    datos_calificaciones = {
        "labels": calificaciones_counts.index.tolist(),
        "data": [float(x) if not pd.isna(x) else None for x in calificaciones_counts.values.tolist()]
    }
    
    # Calificaciones por categoría
    cat_avg = df.groupby('categoria')['calificacion'].mean().sort_values(ascending=False)
    datos_categorias = {
        "labels": cat_avg.index.tolist(),
        "data": [float(x) if not pd.isna(x) else None for x in cat_avg.values.tolist()]
    }
    
    # Calificaciones por grupo de edad - Usar solo filas con grupo_edad válido
    if not df_con_edad.empty and 'grupo_edad' in df_con_edad.columns:
        edad_avg = df_con_edad.groupby('grupo_edad', observed=False)['calificacion'].mean().sort_index()
        datos_edad = {
            "labels": edad_avg.index.astype(str).tolist(),
            "data": [float(x) if not pd.isna(x) else None for x in edad_avg.values.tolist()]
        }
    else:
        datos_edad = {"labels": [], "data": []}
    
    # Calificaciones por sexo
    sexo_avg = df.groupby('sexo')['calificacion'].mean()
    datos_sexo = {
        "labels": sexo_avg.index.tolist(),
        "data": [float(x) if not pd.isna(x) else None for x in sexo_avg.values.tolist()]
    }
    
    # Datos para gráfico de radar
    cat_radar = df.groupby('categoria')['calificacion'].mean()
    datos_radar = {
        "labels": cat_radar.index.tolist(),
        "data": [float(x) if not pd.isna(x) else None for x in cat_radar.values.tolist()]
    }
    
    # Tendencia temporal
    df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
    # Filtrar filas con fechas válidas
    df_con_fecha = df.dropna(subset=['fecha'])
    if not df_con_fecha.empty:
        df_con_fecha['fecha_mes'] = df_con_fecha['fecha'].dt.to_period('M')
        tendencia = df_con_fecha.groupby('fecha_mes')['calificacion'].mean()
        tendencia.index = tendencia.index.astype(str)
        datos_tendencia = {
            "labels": tendencia.index.tolist(),
            "data": [float(x) if not pd.isna(x) else None for x in tendencia.values.tolist()]
        }
    else:
        datos_tendencia = {"labels": [], "data": []}
    
    # Datos para correlación
    # Preparar datos para heatmap de correlación
    datasets = []
    if not user_cat_avg.empty and user_cat_avg.shape[1] > 1:
        cat_corr = user_cat_avg.corr()
        for i, categoria in enumerate(cat_corr.index):
            data = []
            for j, cat_col in enumerate(cat_corr.columns):
                val = cat_corr.loc[categoria, cat_col]
                # Reemplazar NaN con None para evitar errores de JSON
                val = None if pd.isna(val) else float(val)
                data.append({
                    "x": cat_col,
                    "y": categoria,
                    "v": round(val, 2) if val is not None else None
                })
            datasets.append({
                "label": categoria,
                "data": data
            })
    
    datos_correlacion = {
        "labels": user_cat_avg.columns.tolist() if not user_cat_avg.empty else [],
        "datasets": datasets
    }
    
    # Usar json.dumps con cls=NpEncoder para manejar valores NaN
    import json  # Usar el módulo json estándar de Python
    import numpy as np
    
    class NpEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, np.integer):
                return int(obj)
            if isinstance(obj, np.floating):
                return float(obj)
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            if pd.isna(obj):
                return None
            return super(NpEncoder, self).default(obj)
    
    return render_template('admin_analisis.html', 
                         categorias=categorias,
                         grupos_edad=grupos_edad,
                         sexos=sexos,
                         promedio_general=promedio_general,
                         desviacion_estandar=desviacion_estandar,
                         total_respuestas=total_respuestas,
                         usuarios_unicos=usuarios_unicos,
                         top_categorias=top_categorias,
                         bottom_categorias=bottom_categorias,
                         diferencias_demograficas=diferencias_demograficas,
                         correlaciones_importantes=correlaciones_importantes,
                         datos_calificaciones=json.dumps(datos_calificaciones, cls=NpEncoder),
                         datos_categorias=json.dumps(datos_categorias, cls=NpEncoder),
                         datos_edad=json.dumps(datos_edad, cls=NpEncoder),
                         datos_sexo=json.dumps(datos_sexo, cls=NpEncoder),
                         datos_radar=json.dumps(datos_radar, cls=NpEncoder),
                         datos_tendencia=json.dumps(datos_tendencia, cls=NpEncoder),
                         datos_correlacion=json.dumps(datos_correlacion, cls=NpEncoder))

# Modificar la función filtrar_analisis para manejar valores NaN
@app.route('/admin/filtrar_analisis', methods=['POST'])
@admin_required
def filtrar_analisis():
    categoria = request.form.get('categoria', 'todas')
    edad = request.form.get('edad', 'todos')
    sexo = request.form.get('sexo', 'todos')
    
    with sqlite3.connect("database.db") as conn:
        df = pd.read_sql_query("SELECT * FROM respuestas", conn)
    
    # Convertir edad a numérico y crear grupos de edad
    df['edad'] = pd.to_numeric(df['edad'], errors='coerce')
    
    # Crear grupos de edad solo para filas con edad válida
    df_con_edad = df.dropna(subset=['edad'])
    df_con_edad['grupo_edad'] = pd.cut(
        df_con_edad['edad'], 
        bins=[0, 25, 35, 45, 55, 100], 
        labels=['18-25', '26-35', '36-45', '46-55', '56+'], 
        right=False
    )
    
    # Aplicar filtros
    if categoria != 'todas':
        df = df[df['categoria'] == categoria]
        if not df.empty and 'grupo_edad' in df_con_edad.columns:
            df_con_edad = df_con_edad[df_con_edad['categoria'] == categoria]
    
    if edad != 'todos':
        # Filtrar solo en el dataframe con edades válidas
        df_con_edad = df_con_edad[df_con_edad['grupo_edad'] == edad]
        # Obtener los IDs de usuario que cumplen con el filtro de edad
        usuarios_filtrados = df_con_edad['usuario_id'].unique()
        # Aplicar el filtro al dataframe principal
        df = df[df['usuario_id'].isin(usuarios_filtrados)]
    
    if sexo != 'todos':
        df = df[df['sexo'] == sexo]
        if not df.empty and 'grupo_edad' in df_con_edad.columns:
            df_con_edad = df_con_edad[df_con_edad['sexo'] == sexo]
    
    # Si no hay datos después de filtrar
    if df.empty:
        return jsonify({
            'promedio_general': 0,
            'desviacion_estandar': 0,
            'total_respuestas': 0,
            'usuarios_unicos': 0,
            'insights': {
                'top_categorias': [],
                'bottom_categorias': [],
                'diferencias_demograficas': [],
                'correlaciones_importantes': []
            },
            'graficos': {}
        })
    
    # Calcular estadísticas con los datos filtrados
    promedio_general = float(df['calificacion'].mean())
    desviacion_estandar = float(df['calificacion'].std())
    total_respuestas = len(df)
    usuarios_unicos = df['usuario_id'].nunique()
    
    # Calcular insights
    # Top y bottom categorías
    cat_avg = df.groupby('categoria')['calificacion'].mean()
    top_categorias = [{"nombre": cat, "valor": float(val) if not pd.isna(val) else None} for cat, val in cat_avg.nlargest(3).items()]
    bottom_categorias = [{"nombre": cat, "valor": float(val) if not pd.isna(val) else None} for cat, val in cat_avg.nsmallest(3).items()]
    
    # Diferencias demográficas
    diferencias_demograficas = []
    
    # Por sexo (si hay más de un sexo en los datos filtrados)
    if df['sexo'].nunique() > 1:
        sexo_avg = df.groupby('sexo')['calificacion'].mean()
        sexo_diff = sexo_avg.max() - sexo_avg.min()
        if sexo_diff > 0.5:
            sexo_max = sexo_avg.idxmax()
            sexo_min = sexo_avg.idxmin()
            diferencias_demograficas.append(f"Diferencia por sexo: {sexo_diff:.2f} puntos ({sexo_max} > {sexo_min})")
    
    # Por estado civil (si hay más de un estado civil en los datos filtrados)
    if df['estado_civil'].nunique() > 1:
        estado_avg = df.groupby('estado_civil')['calificacion'].mean()
        estado_diff = estado_avg.max() - estado_avg.min()
        if estado_diff > 0.5:
            estado_max = estado_avg.idxmax()
            estado_min = estado_avg.idxmin()
            diferencias_demograficas.append(f"Diferencia por estado civil: {estado_diff:.2f} puntos ({estado_max} > {estado_min})")
    
    # Por grupo de edad (si hay más de un grupo de edad en los datos filtrados)
    if not df_con_edad.empty and 'grupo_edad' in df_con_edad.columns and df_con_edad['grupo_edad'].nunique() > 1:
        edad_avg = df_con_edad.groupby('grupo_edad', observed=False)['calificacion'].mean()
        if not edad_avg.empty and len(edad_avg) > 1:
            edad_diff = edad_avg.max() - edad_avg.min()
            if edad_diff > 0.5:
                edad_max = edad_avg.idxmax()
                edad_min = edad_avg.idxmin()
                diferencias_demograficas.append(f"Diferencia por grupo de edad: {edad_diff:.2f} puntos ({edad_max} > {edad_min})")
    
    # Correlaciones (si hay suficientes datos)
    correlaciones_importantes = []
    if df['usuario_id'].nunique() > 5 and df['categoria'].nunique() > 1:
        user_cat_avg = df.groupby(['usuario_id', 'categoria'])['calificacion'].mean().unstack()
        if not user_cat_avg.empty and user_cat_avg.shape[1] > 1:
            cat_corr = user_cat_avg.corr()
            for i in range(len(cat_corr.columns)):
                for j in range(i+1, len(cat_corr.columns)):
                    corr_val = cat_corr.iloc[i, j]
                    if not pd.isna(corr_val) and abs(corr_val) > 0.6:
                        tipo = "positiva" if corr_val > 0 else "negativa"
                        correlaciones_importantes.append(f"Correlación {tipo} entre {cat_corr.columns[i]} y {cat_corr.columns[j]}: {corr_val:.2f}")
    
    # Preparar datos para gráficos
    graficos = {}
    
    # 1. Distribución de calificaciones
    calificaciones_counts = df['calificacion'].value_counts().sort_index()
    graficos['calificaciones'] = {
        "labels": calificaciones_counts.index.tolist(),
        "data": [float(x) if not pd.isna(x) else None for x in calificaciones_counts.values.tolist()]
    }
    
    # 2. Calificaciones por categoría
    cat_avg = df.groupby('categoria')['calificacion'].mean().sort_values(ascending=False)
    graficos['categorias'] = {
        "labels": cat_avg.index.tolist(),
        "data": [float(x) if not pd.isna(x) else None for x in cat_avg.values.tolist()]
    }
    
    # 3. Calificaciones por grupo de edad
    if not df_con_edad.empty and 'grupo_edad' in df_con_edad.columns and df_con_edad['grupo_edad'].nunique() > 0:
        edad_avg = df_con_edad.groupby('grupo_edad', observed=False)['calificacion'].mean().sort_index()
        graficos['edad'] = {
            "labels": edad_avg.index.astype(str).tolist(),
            "data": [float(x) if not pd.isna(x) else None for x in edad_avg.values.tolist()]
        }
    
    # 4. Calificaciones por sexo
    if df['sexo'].nunique() > 1:
        sexo_avg = df.groupby('sexo')['calificacion'].mean()
        graficos['sexo'] = {
            "labels": sexo_avg.index.tolist(),
            "data": [float(x) if not pd.isna(x) else None for x in sexo_avg.values.tolist()]
        }
    
    # 5. Datos para gráfico de radar
    cat_radar = df.groupby('categoria')['calificacion'].mean()
    graficos['radar'] = {
        "labels": cat_radar.index.tolist(),
        "data": [float(x) if not pd.isna(x) else None for x in cat_radar.values.tolist()]
    }
    
    # 6. Tendencia temporal
    df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
    df_con_fecha = df.dropna(subset=['fecha'])
    if not df_con_fecha.empty:
        df_con_fecha['fecha_mes'] = df_con_fecha['fecha'].dt.to_period('M')
        tendencia = df_con_fecha.groupby('fecha_mes')['calificacion'].mean()
        tendencia.index = tendencia.index.astype(str)
        graficos['tendencia'] = {
            "labels": tendencia.index.tolist(),
            "data": [float(x) if not pd.isna(x) else None for x in tendencia.values.tolist()]
        }
    
    # 7. Datos para correlación
    if df['usuario_id'].nunique() > 5 and df['categoria'].nunique() > 1:
        user_cat_avg = df.groupby(['usuario_id', 'categoria'])['calificacion'].mean().unstack()
        if not user_cat_avg.empty and user_cat_avg.shape[1] > 1:
            cat_corr = user_cat_avg.corr()
            
            # Preparar datos para heatmap de correlación
            datasets = []
            for i, categoria in enumerate(cat_corr.index):
                data = []
                for j, cat_col in enumerate(cat_corr.columns):
                    val = cat_corr.loc[categoria, cat_col]
                    # Reemplazar NaN con None para evitar errores de JSON
                    val = None if pd.isna(val) else float(val)
                    data.append({
                        "x": cat_col,
                        "y": categoria,
                        "v": round(val, 2) if val is not None else None
                    })
                datasets.append({
                    "label": categoria,
                    "data": data
                })
            
            graficos['correlacion'] = {
                "labels": cat_corr.columns.tolist(),
                "datasets": datasets
            }
    
    # Preparar respuesta
    response = {
        'promedio_general': promedio_general,
        'desviacion_estandar': desviacion_estandar,
        'total_respuestas': total_respuestas,
        'usuarios_unicos': usuarios_unicos,
        'insights': {
            'top_categorias': top_categorias,
            'bottom_categorias': bottom_categorias,
            'diferencias_demograficas': diferencias_demograficas,
            'correlaciones_importantes': correlaciones_importantes
        },
        'graficos': graficos
    }
    
    # Usar jsonify con un encoder personalizado para manejar valores NaN
    import json  # Usar el módulo json estándar de Python
    import numpy as np
    
    class NpEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, np.integer):
                return int(obj)
            if isinstance(obj, np.floating):
                return float(obj)
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            if pd.isna(obj):
                return None
            return super(NpEncoder, self).default(obj)
    
    return app.response_class(
        response=json.dumps(response, cls=NpEncoder),
        status=200,
        mimetype='application/json'
    )

if __name__ == "__main__":
    app.run(debug=True)

