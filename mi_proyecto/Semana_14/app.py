from flask import Flask, render_template, redirect, url_for, flash, request, Blueprint
from datetime import datetime
from models import db, Venta, DetalleVenta, Producto, Cliente
from extension import db
# Asegúrate de que todas las formas necesarias estén importadas
from forms import ProductoForm , RegistroForm, LogoutForm, ClienteForm, VentaForm, LoginForm
from models import Producto, Usuario, Cliente, Venta, Proveedor, DetalleVenta 
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user 
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf.csrf import CSRFProtect
from datetime import datetime
from flask import flash, redirect, url_for
import json


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/inventario_n.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'dev-secret-key'

# 2. Inicializa la instancia 'db' registrándola con la aplicación 'app'.
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login' 
login_manager.login_message = "Debes iniciar sesión para acceder a esta página."

@login_manager.user_loader
def load_user(user_id):
    from models import Usuario
    return Usuario.query.get(int(user_id))

inventario = None

from models import Producto, Usuario
from inventory import Inventario
# ---------------------------------------------------------------------

# Inyectar "now" para usar {{ now().year }} en templates si quieres
@app.context_processor
def inject_forms_and_globals():
    return {'now': datetime.utcnow, 'formulario_de_cierre_de_sesion': LogoutForm()}

# 4. Usa el contexto de la aplicación para ejecutar operaciones de DB al inicio.
with app.app_context():
    db.create_all()
    
    
    if not Usuario.query.filter_by(username='admin').first():
        hashed_password = generate_password_hash('12345', method='scrypt') 
        admin_user = Usuario(username='admin', password_hash=hashed_password)
        db.session.add(admin_user)
        db.session.commit()
    
    inventario = Inventario.cargar_desde_bd()

# ---------------------------------------------------------------------
# --- FUNCIÓN DE AYUDA PARA POBLAR SELECT FIELDS EN VENTA (COLOCADA AQUÍ) ---
# ---------------------------------------------------------------------
def populate_venta_form_choices(form):
   

    clientes = Cliente.query.order_by(Cliente.nombre).all()
    form.cliente_id.choices = [(c.id, c.nombre) for c in clientes]
    if not form.cliente_id.choices:
         # Añade una opción de marcador si no hay clientes
        form.cliente_id.choices = [(0, '--- No hay clientes registrados ---')]

    # Opciones para Productos (para el FieldList)
    productos = Producto.query.order_by(Producto.nombre).all()
    # Las opciones deben tener el ID como valor (coerce=int)
    producto_choices = [(p.id, f"{p.nombre} (Stock: {p.cantidad}, ${p.precio:.2f})") for p in productos]
    if not producto_choices:
        producto_choices = [(0, '--- No hay productos registrados ---')]
        
    # Asignar a CADA sub-formulario existente
    for detalle in form.detalles:
        detalle.producto_id.choices = producto_choices
    
    # IMPORTANTE: Asignar al prototipo que usa la plantilla <template>
    # Esto asegura que el JS pueda clonar una fila con las opciones cargadas.
    if form.detalles.entries:
        form.detalles.entries[0].form.producto_id.choices = producto_choices

    pass 

    return productos 

# ---------------------------------------------------------------------
# --- Rutas de Autenticación (NUEVAS: Solución al BuildError) ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    # 1. Si ya está autenticado, redirige.
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    # Crea el formulario de inicio de sesión
    form = LoginForm()

    if form.validate_on_submit():
        # 2. Busca al usuario
        user = Usuario.query.filter_by(username=form.username.data).first()
        
        # 3. Verifica al usuario y la contraseña
        # check_password_hash requiere que la contraseña guardada use generate_password_hash
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            flash(f'¡Bienvenido, {user.username}!', 'success')
            
            # Redirección a la página que intentaba visitar
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        else:
            flash('Inicio de sesión fallido. Por favor, verifica tu nombre de usuario y contraseña.', 'danger')
    
    # Si es GET o la validación falla, renderiza el formulario
    return render_template('login.html', title='Iniciar Sesión', form=form)


@app.route('/logout', methods=['POST'])
def logout():
    logout_user()
    flash('Has cerrado sesión.', 'info')
    return redirect(url_for('index'))

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    form = RegistroForm()

    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='scrypt')
        new_user = Usuario(username=form.username.data, password_hash=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('¡Registro exitoso! Ahora puedes iniciar sesión.', 'success')
        return redirect(url_for('login'))
    return render_template('registro.html', title='Registro', formulario=form)
    
def usuario(nombre):
    return f'Bienvenido, {nombre}!'

@app.route('/about/')
def about():
    return render_template('about.html', title='Acerca de')

@app.route('/')
def index():

    return render_template('index.html', title='Inicio')

# --- Rutas de Productos ---
@app.route('/productos')
def listar_productos():
        
    q = request.args.get('q', '').strip()
    productos = inventario.buscar_por_nombre(q) if q else inventario.listar_todos()
    return render_template('producto/lista.html', title='Productos', productos=productos, q=q)
    
@app.route('/producto/nuevo', methods=['GET', 'POST'])
def crear_producto():
    form = ProductoForm()
    if form.validate_on_submit():
        try:
            inventario.agregar(
                nombre=form.nombre.data,
                cantidad=form.cantidad.data,
                precio=form.precio.data
            )
            flash('Producto agregado correctamente.', 'success')
            return redirect(url_for('listar_productos'))
        except ValueError as e:
            form.nombre.errors.append(str(e))
    return render_template('producto/form.html', title='Nuevo producto', form=form, modo='crear')

@app.route('/productos/<int:pid>/editar', methods=['GET', 'POST'])
def editar_producto(pid):
    prod = Producto.query.get_or_404(pid) 
    form = ProductoForm(obj=prod)
    if form.validate_on_submit():
        try:
            inventario.actualizar(
                id=pid,
                nombre=form.nombre.data,
                cantidad=form.cantidad.data,
                precio=form.precio.data
            )
            flash('Producto actualizado.', 'success')
            return redirect(url_for('listar_productos'))
        except ValueError as e:
            form.nombre.errors.append(str(e))
    return render_template('producto/form.html', title='Editar producto', form=form, modo='editar')

@app.route('/productos/<int:pid>/eliminar', methods=['POST'])
def eliminar_producto(pid):
    ok = inventario.eliminar(pid)
    flash('Producto eliminado.' if ok else 'Producto no encontrado.', 'info' if ok else 'warning')
    return redirect(url_for('listar_productos'))

@app.route('/clientes')
def listar_clientes():
    clientes = Cliente.query.all() 
    return render_template('clientes/lista.html', title='Clientes', clientes=clientes)

@app.route('/inventario_general')
def inventario_general():
        
    productos = inventario.listar_todos() 
    total_productos_unicos = len(productos)
    valor_total_inventario = 0
    
    productos_bajo_stock = [p for p in productos if p.cantidad < 10]
    
    for p in productos:
        valor_total_inventario += p.cantidad * p.precio
        
    return render_template(
        'inventario/resumen.html', 
        title='Inventario General',
        total_productos=total_productos_unicos,
        valor_total=valor_total_inventario,
        productos_bajo_stock=productos_bajo_stock 
    )

@app.route('/clientes/nuevo', methods=['GET', 'POST'])
def crear_cliente():
    form = ClienteForm()
    if form.validate_on_submit():
        if Cliente.query.filter_by(nombre=form.nombre.data).first():
            form.nombre.errors.append('Ya existe un cliente con ese nombre.')
        elif form.email.data and Cliente.query.filter_by(email=form.email.data).first():
            form.email.errors.append('Ya existe un cliente con ese email.')
        else:
            nuevo_cliente = Cliente(
                nombre=form.nombre.data,
                direccion=form.direccion.data,
                telefono=form.telefono.data,
                email=form.email.data
            )
            db.session.add(nuevo_cliente)
            db.session.commit()
            flash('Cliente agregado correctamente.', 'success')
            return redirect(url_for('listar_clientes'))
            
    return render_template('clientes/form.html', title='Nuevo Cliente', form=form, modo='crear')

@app.route('/clientes/<int:cid>/editar', methods=['GET', 'POST'])
def editar_cliente(cid):
    cliente = Cliente.query.get_or_404(cid)
    form = ClienteForm(obj=cliente)
    
    if form.validate_on_submit():
        if Cliente.query.filter(Cliente.nombre == form.nombre.data, Cliente.id != cid).first():
            form.nombre.errors.append('Ya existe otro cliente con ese nombre.')
        elif form.email.data and Cliente.query.filter(Cliente.email == form.email.data, Cliente.id != cid).first():
            form.email.errors.append('Ya existe otro cliente con ese email.')
        else:
            cliente.nombre = form.nombre.data
            cliente.direccion = form.direccion.data
            cliente.telefono = form.telefono.data
            cliente.email = form.email.data
            
            db.session.commit()
            flash('Cliente actualizado correctamente.', 'success')
            return redirect(url_for('listar_clientes'))
            
    return render_template('clientes/form.html', 
                            title='Editar Cliente', 
                            form=form, 
                            modo='editar')

@app.route('/clientes/<int:cid>/eliminar', methods=['POST'])
def eliminar_cliente(cid):
    cliente = Cliente.query.get(cid)
    
    if cliente:
        db.session.delete(cliente)
        db.session.commit()
        flash(f'Cliente "{cliente.nombre}" eliminado.', 'info')
    else:
        flash('Cliente no encontrado.', 'warning')
        
    return redirect(url_for('listar_clientes'))

@app.route('/proveedores')
def listar_proveedores():
    proveedores = Proveedor.query.order_by(Proveedor.nombre).all()
    return render_template('proveedores/lista.html', title='Proveedores', proveedores=proveedores)

@app.route('/ventas')
def listar_ventas():
    ventas = Venta.query.order_by(Venta.fecha.desc()).all() 
    return render_template('ventas/lista.html', title='Registro de Ventas', ventas=ventas)

@app.route('/ventas/nuevo', methods=['GET', 'POST'])
def crear_venta():
    form = VentaForm()
    
    
    productos_db = populate_venta_form_choices(form)
    
    
    productos_data = {
        str(p.id): float(p.precio) 
        for p in productos_db
    }
    productos_json = json.dumps(productos_data) # Serializar para el JS
    
    
    if form.validate_on_submit():
        
        # **VERIFICACIÓN ADICIONAL**: Asegúrate de que se seleccionó un cliente válido
        if form.cliente_id.data == 0:
            flash('Error: Debes seleccionar un cliente válido.', 'danger')
            # Es importante volver a renderizar con el formulario poblado en caso de error
            return render_template('ventas/form.html', title='Registrar Nueva Venta', form=form, productos_json=productos_json, modo='crear')

        total_venta = 0
        detalles_a_crear = []
        
        try:
            # 1. PRE-VALIDACIÓN y CÁLCULO
            for detalle_data in form.detalles.data:
                producto_id = detalle_data.get('producto_id')
                cantidad_vendida = detalle_data.get('cantidad', 0)
                precio_unitario = detalle_data.get('precio_unitario', 0.00) 
                
                # Buscar el producto para verificar stock
                producto = db.session.get(Producto, producto_id)
                
                # **VERIFICACIÓN ADICIONAL**: Producto válido y no el placeholder (ID 0)
                if not producto or producto_id == 0:
                    raise ValueError('Selecciona un producto válido en todos los detalles de venta.')
                
                # Verificación de Stock CRUCIAL
                if producto.cantidad < cantidad_vendida:
                    raise ValueError(
                        f'Stock insuficiente para {producto.nombre}. '
                        f'Disponible: {producto.cantidad}, Solicitado: {cantidad_vendida}.'
                    )
                
                # Calcular subtotal
                subtotal = cantidad_vendida * precio_unitario
                total_venta += subtotal
                
                detalles_a_crear.append({
                    'producto': producto,
                    'cantidad': cantidad_vendida,
                    'precio_unitario': precio_unitario,
                    'subtotal': subtotal
                })

            # 2. CREACIÓN de Cabecera y Detalles (Transacción)
            
            nueva_venta = Venta(
                cliente_id=form.cliente_id.data,
                total=total_venta,
                fecha=datetime.utcnow()
            )
            db.session.add(nueva_venta)

            for detalle in detalles_a_crear:
                nuevo_detalle = DetalleVenta(
                    venta_id=nueva_venta.id,
                    producto_id=detalle['producto'].id,
                    cantidad=detalle['cantidad'],
                    precio_unitario=detalle['precio_unitario'],
                    subtotal=detalle['subtotal']
                )
                db.session.add(nuevo_detalle)
                
                # Descontar stock
                detalle['producto'].cantidad -= detalle['cantidad']
                
            # 3. COMMIT FINAL
            db.session.commit()
            
            flash('Venta registrada y stock actualizado correctamente.', 'success')
            return redirect(url_for('listar_ventas'))

        except ValueError as e:
            db.session.rollback() 
            flash(f'Error al registrar la venta: {e}', 'danger')
            # En caso de error, volvemos a poblar las opciones antes de renderizar
            populate_venta_form_choices(form)

        except Exception as e:
            db.session.rollback()
            flash(f'Ocurrió un error inesperado al procesar la venta. Detalles: {e}', 'danger')
            # En caso de error, volvemos a poblar las opciones antes de renderizar
            populate_venta_form_choices(form)

    # Renderiza el formulario (para GET o si hay un fallo de validación/rollback)
    return render_template('ventas/form.html', 
                            title='Registrar Nueva Venta', 
                            form=form,
                            productos_json=productos_json,
                            modo='crear')
    
@app.route('/ventas/<int:venta_id>/eliminar', methods=['POST'])
@login_required # Opcional, pero muy recomendado para operaciones sensibles
def eliminar_venta(venta_id):
    # Para Venta: Usamos db.session.get. Necesitas manejar el 404 manualmente.
    venta = db.session.get(Venta, venta_id)
    if not venta:
        from flask import abort
        abort(404) 
                        
        producto = db.session.get(Producto, detalle.producto_id)                                        
                        
        db.session.delete(venta)
        
        # 4. Confirmar la transacción (COMMIT)
        db.session.commit()
        
        flash(f'Venta #{venta_id} eliminada y stock revertido correctamente.', 'success')
    
            
    return redirect(url_for('listar_ventas'))

# --- Rutas de Ventas (Agregar esta) ---

@app.route('/ventas/<int:venta_id>/editar', methods=['GET', 'POST'])
@login_required # Opcional, pero muy recomendado
def editar_venta(venta_id):
    # Cargar la venta existente
    venta = db.session.get(Venta, venta_id)
    if not venta:
        from flask import abort
        abort(404) 
    
    producto = db.session.get(Producto, detalle_antiguo.producto_id)
    producto = db.session.get(Producto, producto_id)
    # Pre-cargar el formulario con los datos de la venta
    # La parte compleja es cargar los detalles en el FieldList de VentaForm
    form = VentaForm(obj=venta) 
    
    # Si es GET, o hay un error en POST
    if request.method == 'GET':
        # 1. Cargar los detalles existentes al formulario
        # Esto requiere una implementación específica en tu VentaForm o aquí para llenar el FieldList
        pass # Lógica de precarga del FieldList (detalles)

    # Lógica de manejo de POST para edición
    if form.validate_on_submit():
        try:
            flash('Venta modificada y stock ajustado correctamente.', 'success')
            return redirect(url_for('listar_ventas'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al modificar la venta: {e}', 'danger')
            #
            for detalle_antiguo in venta.detalles:
                producto = Producto.query.get(detalle_antiguo.producto_id)
                if producto:
                    producto.cantidad += detalle_antiguo.cantidad # Devolver stock
            
            # PASO 2: ELIMINAR DETALLES ANTIGUOS
            # Eliminar todos los DetalleVenta relacionados para recrearlos
            DetalleVenta.query.filter_by(venta_id=venta_id).delete()
            db.session.flush() # Aplica la eliminación antes de agregar nuevos
            
            # PASO 3: PROCESAR NUEVOS DETALLES Y APLICAR NUEVO STOCK
            total_venta_nuevo = 0

            for detalle_data in form.detalles.data:
                producto_id = detalle_data.get('producto_id')
                cantidad_vendida = detalle_data.get('cantidad', 0)
                precio_unitario = detalle_data.get('precio_unitario', 0.00)
                
                # ... [Lógica de validación de stock (similar a crear_venta)] ...
                
                producto = Producto.query.get(producto_id)
                subtotal = cantidad_vendida * precio_unitario
                total_venta_nuevo += subtotal

                nuevo_detalle = DetalleVenta(
                    venta=venta,
                    producto_id=producto_id,
                    cantidad=cantidad_vendida,
                    precio_unitario=precio_unitario,
                    subtotal=subtotal
                )
                db.session.add(nuevo_detalle)
                producto.cantidad -= cantidad_vendida # Descontar nuevo stock
                
            # PASO 4: ACTUALIZAR CABECERA DE VENTA
            venta.cliente_id = form.cliente_id.data
            venta.total = total_venta_nuevo
            db.session.add(venta)
            
            # COMMIT FINAL
            db.session.commit()
            
            flash('Venta modificada y stock ajustado correctamente.', 'success')
            return redirect(url_for('listar_ventas'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al modificar la venta: {e}', 'danger')

    # 2. Poblar opciones y JSON (similar a crear_venta)
    productos_db = populate_venta_form_choices(form)
    productos_data = {str(p.id): float(p.precio) for p in productos_db}
    productos_json = json.dumps(productos_data)
    
    return render_template('ventas/form.html', 
                           title=f'Editar Venta #{venta_id}', 
                           form=form, 
                           productos_json=productos_json,
                           modo='editar')

if __name__ == '__main__':
    app.run(debug=True)


