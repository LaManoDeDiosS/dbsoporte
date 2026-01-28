# =========================================================
# IMPORTS FLASK
# =========================================================
from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    request,
    current_app,
    send_file,
    abort
)
from flask_login import login_required, current_user


# =========================================================
# IMPORTS DEL PROYECTO
# =========================================================
from extensions import db
from models import Orden, Cliente, Adjunto, HistorialOrden
from forms import OrdenForm
from utils.pdf_orden import generar_pdf_orden
from utils.permisos import admin_required
from utils.permisos import roles_required



# =========================================================
# OTROS IMPORTS
# =========================================================
from sqlalchemy import func
from werkzeug.utils import secure_filename
from datetime import datetime
import os


# =========================================================
# BLUEPRINT
# =========================================================
ordenes_bp = Blueprint('ordenes', __name__)


# =========================================================
# LISTADO + CREACIÓN DE ÓRDENES
# =========================================================
@ordenes_bp.route('/', methods=['GET', 'POST'])
@login_required
def ordenes():
    """
    - Lista órdenes
    - Permite búsqueda avanzada
    - Permite crear orden (solo admin)
    """

    # -------------------------
    # FORMULARIO
    # -------------------------
    form = OrdenForm()

    # -------------------------
    # CLIENTES (para select y buscador)
    # -------------------------
    clientes = Cliente.query.order_by(Cliente.nombre).all()
    form.cliente.choices = [(c.id, c.nombre) for c in clientes]

    # -------------------------
    # PARÁMETROS DE BÚSQUEDA
    # -------------------------
    numero_busqueda = request.args.get('numero')
    texto_busqueda = request.args.get('texto')
    cliente_busqueda = request.args.get('cliente_id')

    if cliente_busqueda:
        cliente_busqueda = int(cliente_busqueda)

    # -------------------------
    # CONSULTA BASE
    # -------------------------
    query = Orden.query

    if numero_busqueda:
        query = query.filter(Orden.numero == numero_busqueda)

    if texto_busqueda:
        query = query.filter(
            (Orden.persona_reporta.ilike(f'%{texto_busqueda}%')) |
            (Orden.descripcion.ilike(f'%{texto_busqueda}%'))
        )

    if cliente_busqueda:
        query = query.filter(Orden.cliente_id == cliente_busqueda)

    ordenes = query.order_by(Orden.id.desc()).all()

    if (numero_busqueda or texto_busqueda or cliente_busqueda) and not ordenes:
        flash('No se encontraron órdenes con esos criterios', 'warning')

    # -------------------------
    # PROTECCIÓN POST
    # -------------------------
    if request.method == 'POST' and current_user.rol != 'admin':
        abort(403)

    # -------------------------
    # CREAR ORDEN (SOLO ADMIN)
    # -------------------------
    if current_user.rol == 'admin' and form.validate_on_submit():

        ultimo_numero = db.session.query(func.max(Orden.numero)).scalar()
        nuevo_numero = 1 if ultimo_numero is None else ultimo_numero + 1

        orden = Orden(
            numero=nuevo_numero,
            cliente_id=form.cliente.data,
            persona_reporta=form.persona.data,
            descripcion=form.descripcion.data,
            usuario_id=current_user.id
        )

        db.session.add(orden)
        db.session.commit()

        for archivo in form.archivos.data or []:
            if archivo and archivo.filename:
                nombre_seguro = secure_filename(archivo.filename)
                ruta = os.path.join(current_app.config['UPLOAD_FOLDER'], nombre_seguro)
                archivo.save(ruta)

                adjunto = Adjunto(
                    archivo=nombre_seguro,
                    orden_id=orden.id
                )
                db.session.add(adjunto)

        db.session.commit()
        flash(f'Orden #{nuevo_numero} creada correctamente', 'success')
        return redirect(url_for('ordenes.ordenes'))

    # -------------------------
    # RENDER
    # -------------------------
    return render_template(
        'ordenes.html',
        form=form,
        ordenes=ordenes,
        clientes=clientes,
        numero_busqueda=numero_busqueda,
        texto_busqueda=texto_busqueda,
        cliente_busqueda=cliente_busqueda
    )



# =========================================================
# EDITAR ORDEN + HISTORIAL
# =========================================================
@ordenes_bp.route('/<int:orden_id>/editar', methods=['GET', 'POST'])
@login_required
@roles_required('admin', 'tecnico')
def editar_orden(orden_id):

    orden = Orden.query.get_or_404(orden_id)

    if orden.estado == 'cerrada':
        flash('Esta orden está cerrada y no puede ser modificada.', 'warning')
        return redirect(url_for('ordenes.ordenes'))

    form = OrdenForm()

    # 🔴 SIEMPRE cargar choices antes de validar
    clientes = Cliente.query.order_by(Cliente.nombre).all()
    form.cliente.choices = [(c.id, c.nombre) for c in clientes]

    # =====================
    # GET → precargar
    # =====================
    if request.method == 'GET':
        form.cliente.data = orden.cliente_id
        form.persona.data = orden.persona_reporta
        form.descripcion.data = orden.descripcion
        form.solucion.data = orden.solucion
        form.estado.data = orden.estado

    # =====================
    # POST → guardar
    # =====================
    if request.method == 'POST':

        # 🔐 VALIDACIÓN MANUAL SEGÚN ROL
        if current_user.rol == 'admin':
            if not form.cliente.data or not form.persona.data or not form.descripcion.data:
                flash('Todos los campos son obligatorios', 'danger')
                return render_template('orden_editar.html', form=form, orden=orden)

            orden.cliente_id = form.cliente.data
            orden.persona_reporta = form.persona.data
            orden.descripcion = form.descripcion.data

        # Técnico y admin
        orden.solucion = form.solucion.data
        orden.estado = form.estado.data
        orden.ultimo_editor_id = current_user.id
        orden.fecha_actualizacion = datetime.utcnow()

        db.session.commit()

        flash('Orden actualizada correctamente', 'success')
        return redirect(url_for('ordenes.ordenes'))

    return render_template('orden_editar.html', form=form, orden=orden)



# =========================================================
# ELIMINAR ORDEN (SOLO ADMIN)
# =========================================================
@ordenes_bp.route('/<int:orden_id>/eliminar', methods=['POST'])
@login_required
@roles_required('admin')
def eliminar_orden(orden_id):
    """
    Elimina una orden del sistema
    Solo permitido para admin
    """

    orden = Orden.query.get_or_404(orden_id)

    db.session.delete(orden)
    db.session.commit()

    flash(f'Orden #{orden.numero} eliminada correctamente', 'success')
    return redirect(url_for('ordenes.ordenes'))



# =========================================================
# DESCARGAR PDF DE LA ORDEN
# =========================================================
@ordenes_bp.route('/<int:orden_id>/pdf')
@login_required
def descargar_pdf_orden(orden_id):
    """
    Genera y descarga el PDF de una orden
    """

    orden = Orden.query.get_or_404(orden_id)

    ruta_pdf = os.path.join(
        current_app.root_path,
        'static',
        'pdf',
        f'orden_{orden.numero}.pdf'
    )

    # Crear carpeta si no existe
    os.makedirs(os.path.dirname(ruta_pdf), exist_ok=True)

    # Generar PDF
    generar_pdf_orden(orden, ruta_pdf)

    # Enviar al navegador
    return send_file(
        ruta_pdf,
        as_attachment=True,
        download_name=f'orden_{orden.numero}.pdf'
    )

