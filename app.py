# ----------- CARGAR .ENV (SIEMPRE PRIMERO) -----------
from dotenv import load_dotenv
load_dotenv()

# ----------- Librerías estándar de Python -----------
import os
from datetime import datetime

# ----------- Librerías externas -----------
import pymysql

# ----------- Flask y extensiones -----------
from flask import (
    Flask,
    render_template,
    redirect,
    url_for,
    flash,
    request,
    send_file
)
from flask_login import LoginManager, login_required
from flask_wtf import CSRFProtect

# ----------- Archivos del proyecto -----------
from extensions import db, migrate
from models import Usuario, Cliente, Orden
from forms import OrdenForm
from config import DevelopmentConfig

from routes.auth import auth_bp
from routes.ordenes import ordenes_bp
from routes.clientes import clientes_bp
from routes.adjuntos import adjuntos_bp

# ----------- CONFIGURACIÓN APP -----------
app = Flask(__name__)
app.config.from_object(DevelopmentConfig)

# ----------- CSRF GLOBAL -----------
csrf = CSRFProtect(app)

# ----------- MYSQL -----------
pymysql.install_as_MySQLdb()

# ----------- UPLOADS -----------
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# ----------- DATABASE -----------
db.init_app(app)
migrate.init_app(app, db)

# ----------- LOGIN -----------
login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = "Debes iniciar sesión para acceder al sistema"
login_manager.login_message_category = "warning"


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(Usuario, int(user_id))


# ----------- BLUEPRINTS -----------
app.register_blueprint(auth_bp)
app.register_blueprint(ordenes_bp, url_prefix='/ordenes')
app.register_blueprint(clientes_bp)
app.register_blueprint(adjuntos_bp)


# ----------- HOME -----------
@app.route('/')
@login_required
def index():
    return redirect(url_for('ordenes.ordenes'))




# ----------- ERROR 403 -----------
@app.errorhandler(403)
def forbidden(e):
    return render_template('403.html'), 403


# ----------- RUN -----------
if __name__ == '__main__':
    app.run(debug=True)
