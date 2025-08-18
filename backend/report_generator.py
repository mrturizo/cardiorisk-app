"""
Generación de reporte PDF profesional usando reportlab
"""

import os
from datetime import datetime
from typing import Dict, List

from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.lib import colors

OUTPUT_DIR = "backend/reports"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def build_pdf_report(patient: Dict, result: Dict, warnings: List[str]) -> str:
    """
    Crea un PDF, devuelve la ruta al archivo.
    """
    filename = f"reporte_{datetime.utcnow().timestamp()}.pdf"
    path = os.path.join(OUTPUT_DIR, filename)
    doc = SimpleDocTemplate(path, pagesize=LETTER, rightMargin=72,
                            leftMargin=72, topMargin=72, bottomMargin=18)
    styles = getSampleStyleSheet()
    elements = []

    title = Paragraph("Calculadora de Riesgo Cardiovascular", styles["Title"])
    elements.append(title)
    elements.append(Spacer(1, 0.3*inch))

    # ­Datos del paciente
    elements.append(Paragraph("Datos del Paciente", styles["Heading2"]))
    data_tbl = [[k.capitalize().replace("_", " "), v] for k, v in patient.items()]
    tbl = Table(data_tbl, colWidths=[200, 200])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.black),
    ]))
    elements.append(tbl)
    elements.append(Spacer(1, 0.2*inch))

    # ­Resultados
    elements.append(Paragraph("Resultados", styles["Heading2"]))
    res_data = [[k.upper(), f'{v["percent"]} % ({v["category"]})'] for k, v in result.items()]
    tbl2 = Table(res_data, colWidths=[200, 200])
    tbl2.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.black),
    ]))
    elements.append(tbl2)
    elements.append(Spacer(1, 0.2*inch))

    # ­Advertencias
    if warnings:
        elements.append(Paragraph("Advertencias", styles["Heading2"]))
        for w in warnings:
            elements.append(Paragraph(f"- {w}", styles["BodyText"]))
        elements.append(Spacer(1, 0.2*inch))

    # ­Disclaimer
    disclaimer = ("Esta calculadora es una herramienta de apoyo educativo. "
                  "Los resultados no sustituyen el criterio médico profesional. "
                  "Consulte siempre con un profesional de la salud para decisiones médicas.")
    elements.append(Paragraph(disclaimer, styles["Italic"]))
    doc.build(elements)
    return path
