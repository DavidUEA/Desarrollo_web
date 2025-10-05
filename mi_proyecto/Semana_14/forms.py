
from flask_wtf import FlaskForm
from wtforms import Form, SelectField, IntegerField, FloatField, FieldList, FormField, SubmitField,  DecimalField, StringField, PasswordField   
from wtforms.validators import DataRequired, NumberRange, Length, EqualTo, ValidationError, Optional, Email

from models import Usuario 


class ProductoForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired(), Length(max=120)])
    cantidad = IntegerField('Cantidad', validators=[DataRequired(), NumberRange(min=0)])
    precio = DecimalField('Precio', places=2, validators=[DataRequired(), NumberRange(min=0.0)])
    submit = SubmitField('Guardar')

class LoginForm(FlaskForm):
    username = StringField('Nombre de Usuario', validators=[DataRequired()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    submit = SubmitField('Iniciar Sesión')

class RegistroForm(FlaskForm):
    # CRÍTICO: Este form DEBE estar fuera de ProductoForm
    username = StringField('Nombre de Usuario', validators=[
        DataRequired(), 
        Length(min=4, max=25)
    ])
    # CRÍTICO: PasswordField requiere ser importado
    password = PasswordField('Contraseña', validators=[
        DataRequired(), 
        Length(min=6)
    ])
    # CRÍTICO: EqualTo requiere ser importado
    confirm_password= PasswordField('Confirmar Contraseña', validators=[
        DataRequired(), 
        EqualTo('password', message='Las contraseñas deben coincidir')
    ])
    submit = SubmitField('Registrar')

    # Validador personalizado para chequear si el usuario ya existe
    def validate_username(self, username):
        # La validación requiere importar Usuario y ValidationError
        user = Usuario.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Ese nombre de usuario ya está en uso. Por favor, elige otro.')
        
class LogoutForm(FlaskForm):
    # Un formulario simple para propósitos de CSRF y envío POST
    submit = SubmitField('Cerrar Sesión')

class ClienteForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired(), Length(max=100)])
    direccion = StringField('Dirección', validators=[Optional(), Length(max=200)])
    telefono = StringField('Teléfono', validators=[Optional(), Length(max=20)])
    email = StringField('Email', validators=[Optional(), Email(), Length(max=120)])
    submit = SubmitField('Guardar Cliente')

from flask_wtf import FlaskForm
from wtforms import SubmitField, IntegerField, SelectField, FloatField, FieldList, FormField
from wtforms.validators import DataRequired, NumberRange

# (Necesitas obtener la lista de clientes para el SelectField)
from models import Cliente, Producto 

class DetalleVentaForm(FlaskForm):
    # Esto representaría un producto específico en la venta
    producto_id = SelectField('Producto', validators=[DataRequired()], coerce=int)
    cantidad = IntegerField('Cantidad', validators=[DataRequired(), NumberRange(min=1)])
    precio_unitario = DecimalField('Precio Unitario', places=2, validators=[DataRequired(), NumberRange(min=0.0)])
    # No necesitas SubmitField aquí

class VentaForm(FlaskForm):
    # Campo para seleccionar el Cliente
    cliente_id = SelectField('Cliente', validators=[DataRequired()], coerce=int)
    
    # Campo para manejar una lista dinámica de productos (DetalleVentaForm)
    # min_entries=1 asegura que siempre haya al menos un producto listado
    detalles = FieldList(FormField(DetalleVentaForm), min_entries=1) 
    
    submit = SubmitField('Registrar Venta')

    # Este método ayuda a llenar los SelectField con datos de la base de datos
    def __init__(self, *args, **kwargs):
        super(VentaForm, self).__init__(*args, **kwargs)
        
        pass
