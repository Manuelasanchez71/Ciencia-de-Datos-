from flask import Flask, render_template, request, jsonify, send_file
import sqlite3
import pandas as pd
import io
import os

app = Flask(__name__)

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
        conn.commit()

init_db()

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/guardar', methods=['POST'])
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