from flask import Flask , render_template

app = Flask(__name__)

@app.route('/')
def index():
    #"Hello, World!"
    return render_template (index.html, title='Inicio')


@app.route('/usuarios/<nombre>')
def usuario(nombre):
    return f"Hola, {nombre}!"

@app.route('/about')
def about():
    return render_template('about.html', title='Acerca de')

@app.route('/contacto')
def contact():
    return "contacto con nommbres"

if __name__ == '__main__':
    app.run(debug=True)