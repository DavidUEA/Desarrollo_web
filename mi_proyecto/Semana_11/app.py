from flask import Flask , render_template,  redirect, url_for, flash, request
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, length
from wtforms import StringField, SubmitField

app = Flask(__name__)

app.config['SECRET_KEY'] = 'mi_clave_secreta_123'

@app.route('/')
def index():
    #"Hello, World!"
    return render_template ('index.html', title='Inicio')

app.route('/producto/nuevo', methods=['GET', 'POST'])
def nuevo_producto():
    class ProductoForm(FlaskForm):
        nombre = StringField('Nombre del producto', validators=[DataRequired(), length(min=2, max=50)])
        submit = SubmitField('Agregar Producto')

    form = ProductoForm()
    if form.validate_on_submit():
        nombre_producto = form.nombre.data
        flash(f'Producto "{nombre_producto}" agregado exitosamente!', 'success')
        return redirect(url_for('index'))
    
    return render_template('producto_form.html', title='Nuevo Producto', form=form)


@app.route('/usuarios/<nombre>')
def usuario(nombre):
    return f"Hola, {nombre}!"

@app.route('/about')
def about():
    return render_template('about.html', title='Acerca de')

@app.route('/productos')
def listar_productos():
    return "contacto con nosotros en"

if __name__ == '__main__':
    app.run(debug=True)