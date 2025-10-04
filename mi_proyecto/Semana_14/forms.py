
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, DecimalField, SubmitField, PasswordField 
from wtforms.validators import DataRequired, NumberRange, Length, EqualTo, ValidationError, Optional, Email

from models import Usuario 


class ProductoForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired(), Length(max=120)])
    cantidad = IntegerField('Cantidad', validators=[DataRequired(), NumberRange(min=0)])
    precio = DecimalField('Precio', places=2, validators=[DataRequired(), NumberRange(min=0.0)])
    submit = SubmitField('Guardar')

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

