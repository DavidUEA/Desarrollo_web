from flask import Flask , render_template
from flask_wtf import FlaskForm
from wtforms.fields import StringField, PasswordField, SubmitField
app = Flask(__name__)

@app.route('/')
def index():
    #"Hello, World!"
    return render_template ('index.html', title='Inicio')

class loginForm(FlaskForm):
    passusername = StringField('Nomnre del usuario')
    passpassword = PasswordField('Contraseña')
    submit = SubmitField('Enviar datos')

@app.route('/usuarios/<nombre>')
def usuario(nombre):
    return f"Hola, {nombre}!"

@app.route('/about')
def about():
    return render_template('about.html', title='Acerca de')

@app.route('/contacto')
def contacto():
    return "contacto con nosotros en"

if __name__ == '__main__':
    app.run(debug=True)