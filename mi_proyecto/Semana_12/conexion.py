from flask import Flask
from conexion.conexion import get_db_connection

app = Flask(__name__)

@app.route('/test_db')
def test_db():
    try:
        conn = get_db_connection()
        conn.close()
        return '¡Conexión a la base de datos MySQL exitosa!'
    except Exception as e:
        return f'Error al conectar a la base de datos: {e}'

if __name__ == '__main__':
    app.run(debug=True)