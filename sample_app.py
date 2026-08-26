from flask import Flask, render_template, request, redirect, jsonify
import mysql.connector
import os
import time

app = Flask(__name__)

DB_HOST = os.getenv("DB_HOST", "servidor-bd")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_NAME = os.getenv("DB_NAME", "adso_db")
DB_USER = os.getenv("DB_USER", "adso_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "adso_pass")

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS aprendices (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre_completo VARCHAR(100) NOT NULL,
    numero_documento VARCHAR(20) NOT NULL,
    ficha VARCHAR(20) NOT NULL,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""


def get_db_connection(retries=10, delay=3):
    for attempt in range(1, retries + 1):
        try:
            return mysql.connector.connect(
                host=DB_HOST,
                port=DB_PORT,
                database=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD,
                autocommit=True,
            )
        except mysql.connector.Error as err:
            if attempt == retries:
                raise
            time.sleep(delay)


def init_db():
    connection = get_db_connection()
    with connection.cursor() as cursor:
        cursor.execute(CREATE_TABLE_SQL)
    connection.close()


@app.route("/", methods=["GET"])
def index():
    connection = get_db_connection()
    with connection.cursor(dictionary=True) as cursor:
        cursor.execute("SELECT * FROM aprendices ORDER BY creado_en DESC")
        aprendices = cursor.fetchall()
    connection.close()
    return render_template("index.html", aprendices=aprendices)


@app.route("/registrar", methods=["POST"])
def registrar():
    nombre_completo = request.form.get("nombre_completo", "").strip()
    numero_documento = request.form.get("numero_documento", "").strip()
    ficha = request.form.get("ficha", "").strip()

    if not nombre_completo or not numero_documento or not ficha:
        return redirect("/")

    connection = get_db_connection()
    with connection.cursor() as cursor:
        cursor.execute(
            "INSERT INTO aprendices (nombre_completo, numero_documento, ficha) VALUES (%s, %s, %s)",
            (nombre_completo, numero_documento, ficha),
        )
        connection.commit()
    connection.close()
    return redirect("/")


@app.route("/api/aprendices", methods=["GET"])
def api_aprendices():
    connection = get_db_connection()
    with connection.cursor(dictionary=True) as cursor:
        cursor.execute("SELECT * FROM aprendices ORDER BY creado_en DESC")
        aprendices = cursor.fetchall()
    connection.close()
    return jsonify(aprendices)


@app.route("/api/registrar", methods=["POST"])
def api_registrar():
    data = request.get_json(silent=True) or request.form
    nombre_completo = data.get("nombre_completo", "").strip()
    numero_documento = data.get("numero_documento", "").strip()
    ficha = data.get("ficha", "").strip()

    if not nombre_completo or not numero_documento or not ficha:
        return jsonify({"error": "Faltan campos obligatorios"}), 400

    connection = get_db_connection()
    with connection.cursor() as cursor:
        cursor.execute(
            "INSERT INTO aprendices (nombre_completo, numero_documento, ficha) VALUES (%s, %s, %s)",
            (nombre_completo, numero_documento, ficha),
        )
        connection.commit()
    connection.close()
    return jsonify({"mensaje": "Aprendiz registrado correctamente"}), 201


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5050, debug=False)
