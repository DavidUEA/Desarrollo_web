from flask import Flask, render_template, redirect, url_for, flash, request
from datetime import datetime
# 1. Importa la instancia 'db' de SQLAlchemy (aún no inicializada)
from extension import db
from forms import ProductoForm , RegistroForm, LogoutForm, ClienteForm
from models import Producto, Usuario, Cliente # Necesario para crear tablas
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user 
from werkzeug.security import generate_password_hash, check_password_hash
from flask import request
from flask_wtf.csrf import CSRFProtect
from datetime import datetime


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventario_n.db'
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
    # Flask-Login espera que devuelvas un objeto Usuario o None.
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
        # Usa un hash simple (puedes reemplazar 'password' con cualquier hash temporal)
        hashed_password = generate_password_hash('12345', method='scrypt') 
        admin_user = Usuario(username='admin', password_hash=hashed_password)
        db.session.add(admin_user)
        db.session.commit()
    
    # Esta llamada ahora es segura porque 'db' está completamente configurado.
    inventario = Inventario.cargar_desde_bd()

# --- Rutas de Autenticación (NUEVAS: Solución al BuildError) ---

@app.route('/login')
def login():
    
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    user = Usuario.query.filter_by(username='admin').first()
    if user:
        login_user(user)        
        flash('¡Sesión iniciada como admin de prueba!', 'success')
        # Redirige al destino original o a la página de inicio
        next_page = request.args.get('next')
        return redirect(next_page or url_for('index'))
        
    flash('Error: No se pudo iniciar sesión. ¿Falta el usuario "admin"?', 'danger')
    return redirect(url_for('index')) # Fallback seguro

@app.route('/logout', methods=['POST'])
def logout():
    # No requiere @login_required si se usa solo como un enlace
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
            # Aquí se maneja el error de nombre duplicado
            form.nombre.errors.append(str(e))
    return render_template('producto/form.html', title='Nuevo producto', form=form, modo='crear')

@app.route('/productos/<int:pid>/editar', methods=['GET', 'POST'])
def editar_producto(pid):
    # Nota: Usamos Producto.query.get_or_404(pid) para obtener la instancia más reciente,
    # aunque inventario.actualizar también la busca si no está en la caché.
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
    
    # NUEVA LÓGICA: Encontrar productos con bajo stock (Umbral < 10)
    productos_bajo_stock = [p for p in productos if p.cantidad < 10]
    
    for p in productos:
        valor_total_inventario += p.cantidad * p.precio
        
    return render_template(
        'inventario/resumen.html', 
        title='Inventario General',
        total_productos=total_productos_unicos,
        valor_total=valor_total_inventario,
            # Pasar la nueva lista a la plantilla
        productos_bajo_stock=productos_bajo_stock 
    )

@app.route('/ventas')
def listar_ventas():
    # NOTA: Aquí iría la lógica para obtener la lista de ventas.
    ventas = []
    return render_template('ventas/lista.html', title='Registro de Ventas', ventas=ventas)

@app.route('/proveedores')
def listar_proveedores():
    # NOTA: Aquí iría la lógica para obtener la lista de proveedores.
    proveedores = []
    return render_template('proveedores/lista.html', title='Proveedores', proveedores=proveedores)

@app.route('/clientes/nuevo', methods=['GET', 'POST'])
# @login_required # Puedes añadir esto si requieres autenticación
def crear_cliente():
    form = ClienteForm()
    if form.validate_on_submit():
        # 1. Verificar si el nombre ya existe
        if Cliente.query.filter_by(nombre=form.nombre.data).first():
            form.nombre.errors.append('Ya existe un cliente con ese nombre.')
        # 2. Verificar si el email ya existe (si se proporcionó)
        elif form.email.data and Cliente.query.filter_by(email=form.email.data).first():
            form.email.errors.append('Ya existe un cliente con ese email.')
        else:
            # 3. Crear y guardar el nuevo cliente
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
            
    # La plantilla para crear/editar puede ser la misma: 'clientes/form.html'
    return render_template('clientes/form.html', title='Nuevo Cliente', form=form, modo='crear')

@app.route('/clientes/<int:cid>/editar', methods=['GET', 'POST'])
# @login_required # Puedes proteger la ruta si es necesario
def editar_cliente(cid):
    # Obtener el cliente de la base de datos o lanzar 404
    cliente = Cliente.query.get_or_404(cid)
    
    # Pre-llenar el formulario con los datos del cliente
    form = ClienteForm(obj=cliente)
    
    if form.validate_on_submit():
        # Verificar si el nombre o email ya existen en otro cliente
        if Cliente.query.filter(Cliente.nombre == form.nombre.data, Cliente.id != cid).first():
            form.nombre.errors.append('Ya existe otro cliente con ese nombre.')
        elif form.email.data and Cliente.query.filter(Cliente.email == form.email.data, Cliente.id != cid).first():
            form.email.errors.append('Ya existe otro cliente con ese email.')
        else:
            # Actualizar los datos del cliente
            cliente.nombre = form.nombre.data
            cliente.direccion = form.direccion.data
            cliente.telefono = form.telefono.data
            cliente.email = form.email.data
            
            db.session.commit()
            flash('Cliente actualizado correctamente.', 'success')
            return redirect(url_for('listar_clientes'))
            
    # Renderizar el mismo formulario usado para crear
    return render_template('clientes/form.html', 
                           title='Editar Cliente', 
                           form=form, 
                           modo='editar')


@app.route('/clientes/<int:cid>/eliminar', methods=['POST'])
# @login_required # Puedes proteger la ruta si es necesario
def eliminar_cliente(cid):
    cliente = Cliente.query.get(cid)
    
    if cliente:
        db.session.delete(cliente)
        db.session.commit()
        flash(f'Cliente "{cliente.nombre}" eliminado.', 'info')
    else:
        flash('Cliente no encontrado.', 'warning')
        
    return redirect(url_for('listar_clientes'))

if __name__ == '__main__':
    app.run(debug=True)