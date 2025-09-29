
from extension import db 
from flask_login import UserMixin


class Producto(db.Model):
    __tablename__ = 'productos'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(120), unique=True, nullable=False)
    cantidad = db.Column(db.Integer, nullable=False, default=0)
    precio = db.Column(db.Float, nullable=False, default=0.0)

    def __repr__(self):
        return f'<Producto {self.id} {self.nombre}>'

    def to_tuple(self):
        return (self.id, self.nombre, self.cantidad, self.precio)

class Usuario(db.Model, UserMixin):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    pass
    # En una app real, aquí iría un campo 'password_hash'
    
    def __repr__(self):
        return f'<Usuario {self.username}>'