import mysql.connector

HOST = "localhost"
USER = "root"
PASSWORD = ""  # Cambia por tu contraseña de MySQL
DATABASE = "desarrollo_web"

def crear_base_y_tabla():
    # Crear la base de datos si no existe
    conn = mysql.connector.connect(host=HOST, user=USER, password=PASSWORD)
    cursor = conn.cursor()
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DATABASE};")
    cursor.close()
    conn.close()

    # Conectar a la base de datos y crear la tabla usuarios si no existe
    conn = mysql.connector.connect(host=HOST, user=USER, password=PASSWORD, database=DATABASE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id_usuario INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(100) NOT NULL,
            mail VARCHAR(100) NOT NULL
        );
    """ )
    conn.commit()
    cursor.close()
    conn.close()

def obtener_conexion():
    return mysql.connector.connect(
        host=HOST,
        user=USER,
        password=PASSWORD,
        database=DATABASE
    )
