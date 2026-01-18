from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
import os

def generar_pdf_orden(orden, ruta_pdf):
    c = canvas.Canvas(ruta_pdf, pagesize=A4)
    width, height = A4

    y = height - 2 * cm

    c.setFont("Helvetica-Bold", 14)
    c.drawString(2 * cm, y, f"ORDEN DE SERVICIO #{orden.numero}")

    y -= 1.5 * cm
    c.setFont("Helvetica", 10)

    c.drawString(2 * cm, y, f"Cliente: {orden.cliente.nombre}")
    y -= 0.8 * cm

    c.drawString(2 * cm, y, f"Persona que reporta: {orden.persona_reporta}")
    y -= 0.8 * cm

    c.drawString(2 * cm, y, f"Fecha: {orden.fecha.strftime('%Y-%m-%d %H:%M')}")
    y -= 1.2 * cm

    c.setFont("Helvetica-Bold", 10)
    c.drawString(2 * cm, y, "Observaciones:")
    y -= 0.8 * cm

    c.setFont("Helvetica", 10)
    texto = c.beginText(2 * cm, y)
    texto.textLines(orden.descripcion)
    c.drawText(texto)

    y = texto.getY() - 1 * cm

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

    c.showPage()
    c.save()
