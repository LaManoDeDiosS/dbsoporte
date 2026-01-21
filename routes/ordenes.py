# -------- Flask --------
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

# -------- Proyecto --------
from extensions import db
from models import Orden, Cliente, Adjunto
from forms import OrdenForm

# -------- Otros --------
from sqlalchemy import func
from werkzeug.utils import secure_filename
from datetime import datetime
import os
from flask import current_app

ordenes_bp = Blueprint('ordenes', __name__)

@ordenes_bp.route('/ordenes', methods=['GET', 'POST'])
@login_required
def ordenes():
    form = OrdenForm()

    # Cargar clientes
    clientes = Cliente.query.order_by(Cliente.nombre).all()
    form.cliente.choices = [(c.id, c.nombre) for c in clientes]

    lista_ordenes = Orden.query.order_by(Orden.id.desc()).all()

    # Solo admin puede crear órdenes
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
                ruta = os.path.join(current_app.config['UPLOAD_FOLDER'], nombre)
                file.save(ruta)

                adj = Adjunto(archivo=nombre, orden_id=orden.id)
                db.session.add(adj)

        db.session.commit()
        flash(f'Orden #{nuevo_numero} creada correctamente')
        return redirect(url_for('ordenes.ordenes'))

    return render_template('ordenes.html', form=form, ordenes=lista_ordenes)
