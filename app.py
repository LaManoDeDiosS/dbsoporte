# Prueba Git Ok

# ----------- Librerías estándar de Python -----------
import os

# ----------- Librerías externas -----------
import pymysql
from dotenv import load_dotenv
from sqlalchemy import func
from werkzeug.utils import secure_filename

# ----------- Flask y extensiones -----------
from flask import Flask, render_template, redirect, url_for, flash, request,make_response,send_file
from flask_login import LoginManager, login_user, login_required, current_user

# ----------- Archivos del proyecto -----------
from extensions import db, migrate
from models import Usuario, Cliente, Orden, Adjunto
from forms import LoginForm, ClienteForm, OrdenForm
from datetime import datetime
from utils.pdf_orden import generar_pdf_orden


# ------------ CONFIGURACIÓN ------------

load_dotenv()
pymysql.install_as_MySQLdb()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@"
    f"{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db.init_app(app)
migrate.init_app(app, db)

login_manager = LoginManager(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

def cargar_formulario_orden():
    form = OrdenForm()
    clientes = Cliente.query.order_by(Cliente.nombre).all()
    form.cliente.choices = [(c.id, c.nombre) for c in clientes]
    return form

# ------------ LOGIN ------------

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        usuario = Usuario.query.filter_by(email=form.email.data).first()
        if usuario and usuario.password == form.password.data:
            login_user(usuario)

            # 🔹 Admin ve todas las órdenes
            if usuario.rol == 'admin':
                return redirect(url_for('ordenes'))

            # 🔹 Lector también entra a /ordenes pero sin formulario
            return redirect(url_for('ordenes'))

        flash('Correo o contraseña incorrectos')

    return render_template('login.html', form=form)

# ------------ HOME ------------

@app.route('/')
@login_required
def index():
    return redirect(url_for('ordenes'))

# ------------ CLIENTES ------------

@app.route('/clientes', methods=['GET', 'POST'])
@login_required
def clientes():
    if current_user.rol != 'admin':
        flash('No tienes permisos para crear clientes')
        return redirect(url_for('ordenes'))

    form = ClienteForm()
    lista_clientes = Cliente.query.all()

    if form.validate_on_submit():
        nuevo = Cliente(nombre=form.nombre.data)
        db.session.add(nuevo)
        db.session.commit()
        flash('Cliente creado correctamente')
        return redirect(url_for('clientes'))

    return render_template('clientes.html', form=form, clientes=lista_clientes)

# ------------ ORDENES ------------

@app.route('/ordenes', methods=['GET', 'POST'])
@login_required
def ordenes():
    form = OrdenForm()

    clientes = Cliente.query.order_by(Cliente.nombre).all()
    form.cliente.choices = [(c.id, c.nombre) for c in clientes]

    ordenes = Orden.query.order_by(Orden.id.desc()).all()

    # 🔹 Solo admin puede guardar órdenes
    if current_user.rol == 'admin' and form.validate_on_submit():

        ultimo = db.session.query(func.max(Orden.numero)).scalar()
        nuevo_numero = 1 if ultimo is None else ultimo + 1

        orden = Orden(
            numero=nuevo_numero,
            cliente_id=form.cliente.data,
            persona_reporta=form.persona.data,
            descripcion=form.descripcion.data,
            usuario_id=current_user.id,
            fecha=datetime.now()
        )

        db.session.add(orden)
        db.session.commit()

        for file in form.archivos.data:
            if file and file.filename:
                nombre = secure_filename(file.filename)
                ruta = os.path.join(app.config['UPLOAD_FOLDER'], nombre)
                file.save(ruta)

                adj = Adjunto(archivo=nombre, orden_id=orden.id)
                db.session.add(adj)

        db.session.commit()
        flash('Orden creada correctamente')
        return redirect(url_for('ordenes'))

    return render_template('ordenes.html', form=form, ordenes=ordenes)

# ------------ DETALLE DE ORDEN ------------

@app.route('/orden/<int:orden_id>')
@login_required
def detalle_orden(orden_id):
    orden = Orden.query.get_or_404(orden_id)
    return render_template('orden_detalle.html', orden=orden)

# ------------ IMPRIMIR ORDEN ------------

@app.route('/orden/<int:orden_id>/imprimir')
@login_required
def imprimir_orden(orden_id):
    orden = Orden.query.get_or_404(orden_id)
    return render_template('orden_imprimir.html', orden=orden)


# ------------ BUSCADOR ------------
@app.route('/buscar', methods=['GET'])
@login_required
def buscar():
    numero = request.args.get('numero')

    if not numero:
        flash('Debes escribir un número de orden')
        return redirect(url_for('ordenes'))

    ordenes = Orden.query.filter_by(numero=numero).all()

    return render_template('ordenes.html', ordenes=ordenes, form=OrdenForm())

# ------------ ADJUNTAR ------------

@app.route('/adjunto/<int:adjunto_id>/eliminar')
@login_required
def eliminar_adjunto(adjunto_id):

    # 🔒 Seguridad por rol
    if current_user.rol != 'admin':
        flash('No tienes permisos para eliminar archivos')
        return redirect(url_for('ordenes'))

    adjunto = Adjunto.query.get_or_404(adjunto_id)

    # Ruta física del archivo
    ruta = os.path.join(app.config['UPLOAD_FOLDER'], adjunto.archivo)

    # Eliminar archivo del disco
    if os.path.exists(ruta):
        os.remove(ruta)

    # Eliminar registro de la BD
    db.session.delete(adjunto)
    db.session.commit()

    flash('Archivo eliminado correctamente')
    return redirect(url_for('ordenes'))

# ------------ PDF ORDEN ------------

@app.route('/orden/<int:orden_id>/pdf')
@login_required
def descargar_pdf_orden(orden_id):
    orden = Orden.query.get_or_404(orden_id)

    nombre_pdf = f"orden_{orden.numero}.pdf"
    ruta_pdf = os.path.join("static", nombre_pdf)

    generar_pdf_orden(orden, ruta_pdf)

    return send_file(ruta_pdf, as_attachment=True)



# ---------------------------------

if __name__ == '__main__':
    app.run(debug=True)
