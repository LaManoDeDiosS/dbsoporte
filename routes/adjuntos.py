# -------- Librerías --------
import os
from flask import Blueprint, send_from_directory, redirect, url_for, flash
from flask_login import login_required, current_user

# -------- Proyecto --------
from extensions import db
from models import Adjunto
from flask import current_app

adjuntos_bp = Blueprint('adjuntos', __name__)

# ---------------- DESCARGAR ----------------
@adjuntos_bp.route('/adjuntos/descargar/<int:adjunto_id>')
@login_required
def descargar_adjunto(adjunto_id):
    adjunto = Adjunto.query.get_or_404(adjunto_id)

    return send_from_directory(
        current_app.config['UPLOAD_FOLDER'],
        adjunto.archivo,
        as_attachment=True
    )

# ---------------- ELIMINAR ----------------
@adjuntos_bp.route('/adjuntos/eliminar/<int:adjunto_id>')
@login_required
def eliminar_adjunto(adjunto_id):

    # 🔒 Solo admin puede eliminar
    if current_user.rol != 'admin':
        flash('No tienes permisos para eliminar archivos')
        return redirect(url_for('ordenes.ordenes'))

    adjunto = Adjunto.query.get_or_404(adjunto_id)

    # Borrar archivo físico
    ruta = os.path.join(current_app.config['UPLOAD_FOLDER'], adjunto.archivo)
    if os.path.exists(ruta):
        os.remove(ruta)

    # Borrar registro BD
    db.session.delete(adjunto)
    db.session.commit()

    flash('Archivo eliminado correctamente')
    return redirect(url_for('ordenes.ordenes'))
