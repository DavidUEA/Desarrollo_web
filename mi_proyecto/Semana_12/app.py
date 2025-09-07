from flask import Flask, request, redirect, url_for, render_template, flash
from flask_sqlalchemy import SQLAlchemy
import json
import csv
import os

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
database_path = os.path.join(basedir, 'database', 'usuarios.db')
os.makedirs(os.path.dirname(database_path), exist_ok=True)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{database_path}'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'mi_super_clave_secreta'

db = SQLAlchemy(app)


os.makedirs('datos', exist_ok=True)
os.makedirs('database', exist_ok=True)


class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return f'<Usuario {self.nombre}>'


with app.app_context():
    db.create_all()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/guardar-txt', methods=['POST'])
def guardar_txt():
    dato = request.form.get('dato_txt')
    if dato:
        with open('datos/datos.txt', 'a') as f:
            f.write(dato + '\n')
        flash('Dato guardado en TXT.', 'success')
    return redirect(url_for('leer_txt'))

@app.route('/leer-txt')
def leer_txt():
    datos = []
    try:
        with open('datos/datos.txt', 'r') as f:
            for line in f:
                datos.append(line.strip())
    except FileNotFoundError:
        flash('Archivo TXT no encontrado. Crea un dato primero.', 'warning')
    return render_template('resultado.html', titulo='Datos TXT', datos=datos)


# Guardar y leer datos en formato JSON
@app.route('/guardar-json', methods=['POST'])
def guardar_json():
    nombre = request.form.get('nombre_json')
    valor = request.form.get('valor_json')
    nuevo_dato = {'nombre': nombre, 'valor': valor}
    
    datos = []
    try:
        with open('datos/datos.json', 'r') as f:
            datos = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        pass
        
    datos.append(nuevo_dato)
    
    with open('datos/datos.json', 'w') as f:
        json.dump(datos, f, indent=4)
    
    flash('Dato guardado en JSON.', 'success')
    return redirect(url_for('leer_json'))

@app.route('/leer-json')
def leer_json():
    datos = []
    try:
        with open('datos/datos.json', 'r') as f:
            datos = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        flash('Archivo JSON no encontrado o corrupto. Crea un dato primero.', 'warning')
    return render_template('resultado.html', titulo='Datos JSON', datos=datos)


# Guardar y leer datos en formato CSV
@app.route('/guardar-csv', methods=['POST'])
def guardar_csv():
    nombre = request.form.get('nombre_csv')
    precio = request.form.get('precio_csv')
    
    encabezado_existe = os.path.exists('datos/datos.csv') and os.path.getsize('datos/datos.csv') > 0

    with open('datos/datos.csv', 'a', newline='') as f:
        writer = csv.writer(f)
        if not encabezado_existe:
            writer.writerow(['nombre', 'precio'])
        writer.writerow([nombre, precio])
    
    flash('Dato guardado en CSV.', 'success')
    return redirect(url_for('leer_csv'))

@app.route('/leer-csv')
def leer_csv():
    datos = []
    try:
        with open('datos/datos.csv', 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                datos.append(row)
    except FileNotFoundError:
        flash('Archivo CSV no encontrado. Crea un dato primero.', 'warning')
    return render_template('resultado.html', titulo='Datos CSV', datos=datos)


# --- 2.3 Persistencia con SQLite (Continuación) ---
@app.route('/guardar-db', methods=['POST'])
def guardar_db():
    nombre = request.form.get('nombre_db')
    email = request.form.get('email_db')
    
    if nombre and email:
        nuevo_usuario = Usuario(nombre=nombre, email=email)
        try:
            db.session.add(nuevo_usuario)
            db.session.commit()
            flash('Usuario guardado en la base de datos.', 'success')
        except Exception:
            db.session.rollback()
            flash('Error: El nombre o email ya existen.', 'danger')
    
    return redirect(url_for('leer_db'))

@app.route('/leer-db')
def leer_db():
    usuarios = Usuario.query.all()
    return render_template('resultado.html', titulo='Usuarios de la Base de Datos', datos=usuarios)


if __name__ == '__main__':
    app.run(debug=True)