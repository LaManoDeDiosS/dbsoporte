# ----------- Librerías estándar de Python -----------
import os

# ----------- Librerías externas -----------
import pymysql
from dotenv import load_dotenv
from sqlalchemy import func
from werkzeug.utils import secure_filename

# ----------- Flask y extensiones -----------
from flask import Flask, render_template, redirect, url_for, flash, request,make_response,send_file,send_from_directory
from flask_login import LoginManager, login_user, login_required, current_user

# ----------- Archivos del proyecto -----------
from extensions import db, migrate
from models import Usuario, Cliente, Orden, Adjunto
from forms import LoginForm, ClienteForm, OrdenForm
from datetime import datetime


from utils.pdf_orden import generar_pdf_orden
from config import DevelopmentConfig
from routes.auth import auth_bp
from routes.ordenes import  ordenes_bp
from routes.clientes import clientes_bp
from routes.adjuntos import adjuntos_bp

# ------------ CONFIGURACIÓN ------------
app = Flask(__name__)
app.config.from_object(DevelopmentConfig)

# ------------ Login Blueprint------------
app.register_blueprint(auth_bp)

# ------------ ordenes Blueprint------------
app.register_blueprint(ordenes_bp)

#-------------Clientes Blueprint-----------
app.register_blueprint(clientes_bp)

#-------------Adjuntar Blueprint-----------

app.register_blueprint(adjuntos_bp)

load_dotenv()
pymysql.install_as_MySQLdb()


UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db.init_app(app)
migrate.init_app(app, db)

login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(Usuario, int(user_id))


def cargar_formulario_orden():
    form = OrdenForm()
    clientes = Cliente.query.order_by(Cliente.nombre).all()
    form.cliente.choices = [(c.id, c.nombre) for c in clientes]
    return form



# ------------ HOME ------------

@app.route('/')
@login_required
def index():
    return redirect(url_for('ordenes.ordenes'))

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
        return redirect(url_for('ordenes.ordenes'))

    ordenes = Orden.query.filter_by(numero=numero).all()

    return render_template('ordenes.html', ordenes=ordenes, form=OrdenForm())


# ------------ PDF ORDEN ------------

@app.route('/orden/<int:orden_id>/pdf')
@login_required
def descargar_pdf_orden(orden_id):
    orden = Orden.query.get_or_404(orden_id)

    nombre_pdf = f"orden_{orden.numero}.pdf"
    ruta_pdf = os.path.join("static", nombre_pdf)

    generar_pdf_orden(orden, ruta_pdf)

    return send_file(ruta_pdf, as_attachment=True)

# ------------ EDITAR ORDENES------------
@app.route('/orden/<int:orden_id>/editar', methods=['GET', 'POST'])
@login_required
def editar_orden(orden_id):

    if current_user.rol != 'admin':
        flash('No tienes permisos para editar órdenes')
        return redirect(url_for('ver_orden', orden_id=orden_id))

    orden = Orden.query.get_or_404(orden_id)
    form = OrdenForm()

    # Cargar clientes
    clientes = Cliente.query.order_by(Cliente.nombre).all()
    form.cliente.choices = [(c.id, c.nombre) for c in clientes]

    if request.method == 'GET':
        form.cliente.data = orden.cliente_id
        form.persona.data = orden.persona_reporta
        form.descripcion.data = orden.descripcion

    if form.validate_on_submit():
        orden.cliente_id = form.cliente.data
        orden.persona_reporta = form.persona.data
        orden.descripcion = form.descripcion.data

        db.session.commit()
        flash('Orden actualizada correctamente')
        return redirect(url_for('ver_orden', orden_id=orden.id))

    return render_template('orden_editar.html', form=form, orden=orden)


# ---------------------------------

if __name__ == '__main__':
    app.run(debug=True)
