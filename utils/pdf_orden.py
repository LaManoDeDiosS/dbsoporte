from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
import os


def generar_pdf_orden(orden, ruta_pdf):
    c = canvas.Canvas(ruta_pdf, pagesize=A4)
    width, height = A4

    y = height - 2 * cm

    # =========================
    # ENCABEZADO
    # =========================
    c.setFont("Helvetica-Bold", 14)
    c.drawString(2 * cm, y, f"ORDEN DE SERVICIO #{orden.numero}")

    y -= 1.5 * cm
    c.setFont("Helvetica", 10)

    # =========================
    # DATOS PRINCIPALES
    # =========================
    c.drawString(2 * cm, y, f"Cliente: {orden.cliente.nombre}")
    y -= 0.8 * cm

    c.drawString(2 * cm, y, f"Persona que reporta: {orden.persona_reporta}")
    y -= 0.8 * cm

    # 🔥 Fecha de creación (campo que YA tienes)
    c.drawString(
        2 * cm,
        y,
        f"Fecha de creación: {orden.fecha_creacion.strftime('%Y-%m-%d %H:%M')}"
    )
    y -= 1.2 * cm

    # =========================
    # OBSERVACIONES
    # =========================
    c.setFont("Helvetica-Bold", 10)
    c.drawString(2 * cm, y, "Observaciones:")
    y -= 0.8 * cm

    c.setFont("Helvetica", 10)
    texto = c.beginText(2 * cm, y)
    texto.textLines(orden.descripcion)
    c.drawText(texto)

    y = texto.getY() - 1 * cm

    # =========================
    # AUDITORÍA (NUEVO – PASO C)
    # =========================
    c.setFont("Helvetica-Bold", 10)
    c.drawString(2 * cm, y, "Auditoría:")
    y -= 0.8 * cm

    c.setFont("Helvetica", 10)

    # Creador (siempre existe)
    c.drawString(
        2 * cm,
        y,
        f"Creado por: {orden.usuario_creador.email}"
    )
    y -= 0.6 * cm

    # Última edición (NO romper si no existe)
    if orden.fecha_actualizacion and orden.ultimo_editor:
        c.drawString(
            2 * cm,
            y,
            f"Última edición por: {orden.ultimo_editor.email}"
        )
        y -= 0.6 * cm

        c.drawString(
            2 * cm,
            y,
            f"Fecha última edición: {orden.fecha_actualizacion.strftime('%Y-%m-%d %H:%M')}"
        )
    else:
        c.drawString(2 * cm, y, "Última edición: —")

    y -= 1.2 * cm

    # =========================
    # ARCHIVOS ADJUNTOS (MISMA LÓGICA)
    # =========================
    c.setFont("Helvetica-Bold", 10)
    c.drawString(2 * cm, y, "Archivos adjuntos:")
    y -= 0.8 * cm

    c.setFont("Helvetica", 10)

    if orden.adjuntos:
        for adj in orden.adjuntos:
            c.drawString(2.2 * cm, y, f"- {adj.archivo}")
            y -= 0.6 * cm
    else:
        c.drawString(2.2 * cm, y, "No hay archivos adjuntos")

    # =========================
    # FINALIZAR PDF
    # =========================
    c.showPage()
    c.save()
