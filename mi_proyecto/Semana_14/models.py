
from extension import db 
from flask_login import UserMixin
from datetime import datetime


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
    
class Cliente(db.Model):
    __tablename__ = 'cliente'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), unique=True, nullable=False)
    direccion = db.Column(db.String(200), nullable=True)
    telefono = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=True)

    def __repr__(self):
        return f'<Cliente {self.nombre}>'
    
class Proveedor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), unique=True, nullable=False)
    contacto = db.Column(db.String(100))
    telefono = db.Column(db.String(20))
    email = db.Column(db.String(100))
    
    def __repr__(self):
        return f'<Proveedor {self.nombre}>'
    
class Venta(db.Model):
    __tablename__ = 'venta'
    id = db.Column(db.Integer, primary_key=True)
    
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    total = db.Column(db.Float, nullable=False)

    
    cliente = db.relationship('Cliente', backref=db.backref('ventas', lazy=True))

    def __repr__(self):
        return f'<Venta {self.id} - Producto {self.producto_id} - Cliente {self.cliente_id}>'
class DetalleVenta(db.Model):
        __tablename__ = 'detalle_venta'
    
        id = db.Column(db.Integer, primary_key=True)
    
    # Claves Foráneas
        venta_id = db.Column(db.Integer, db.ForeignKey('venta.id'), nullable=False)
        producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False)
    
    # Campos de Datos
        cantidad = db.Column(db.Integer, nullable=False)
        precio_unitario = db.Column(db.Float, nullable=False)
        subtotal = db.Column(db.Float, nullable=False) # Se calcula al registrar

    # Relaciones: permiten acceder al Producto y a la Venta desde el detalle
        venta = db.relationship('Venta', backref=db.backref('detalles', lazy=True))
        producto = db.relationship('Producto', backref=db.backref('detalles_venta', lazy=True))
    
        def __repr__(self):
            return f'<DetalleVenta Venta:{self.venta_id} Producto:{self.producto_id}>'

