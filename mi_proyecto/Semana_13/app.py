from flask import Flask, request, jsonify
from conexion import obtener_conexion, crear_base_y_tabla

app = Flask(__name__)

# Al iniciar la app se crea la BD y la tabla si no existen
crear_base_y_tabla()

@app.route('/')
def home():
    return "Flask funcionando!"

@app.route('/test_db')
def test_db():
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("SELECT DATABASE();")
        db = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return f"Conectado a la BD: {db}"
    except Exception as e:
        return f"Error: {str(e)}"

@app.route('/add_usuario', methods=['POST'])
def add_usuario():
    data = request.get_json()
    nombre = data.get("nombre")
    mail = data.get("mail")
    if not nombre or not mail:
        return jsonify({"error": "Faltan 'nombre' o 'mail'"}), 400

    conn = obtener_conexion()
    cursor = conn.cursor()
    sql = "INSERT INTO usuarios (nombre, mail) VALUES (%s, %s)"
    cursor.execute(sql, (nombre, mail))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"mensaje": "Usuario agregado"}), 201

@app.route('/usuarios', methods=['GET'])
def listar_usuarios():
    conn = obtener_conexion()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM usuarios;")
    filas = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(filas)

if __name__ == '__main__':
    app.run(debug=True)
