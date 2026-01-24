# -------- Flask --------
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

# -------- Proyecto --------
from extensions import db
from models import Orden, Cliente, Adjunto
from forms import OrdenForm

clientes_bp = Blueprint('clientes', __name__)

@clientes_bp.route('/clientes', methods=['GET', 'POST'])
@login_required
def clientes():
    #🔒 Permiso: Solo admin puede crear
    if current_user.rol != 'admin':
        flash('No tienes permisos para crear clientes')
        return redirect(url_for('ordenes.ordenes'))

    form = ClienteForm()
    lista_clientes = Cliente.query.order_by(Cliente.nombre).all()

    if form.validate_on_submit():
        nuevo = Cliente(nombre=form.nombre.data)
        db.session.add(nuevo)
        db.session.commit()
        flash('Cliente creado correctamente')
        return redirect(url_for('clientes.clientes'))

    return render_template('clientes.tml', form=form, clientes=lista_clientes)