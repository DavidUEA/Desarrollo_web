import msql.connector

def conexion():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="semana_8(1)"
    )
def cerrar_conexion(conn):
    if con.is_connected():
        con.close()
        print("Conexión cerrada")}
        if

