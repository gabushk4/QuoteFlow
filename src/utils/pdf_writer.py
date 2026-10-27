from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT

from xml.sax.saxutils import escape
from datetime import date 

from src.models import Submission

PAGE_MARGIN = 40

def generate_pdf(submission: Submission, output_path: Path) -> None:
    doc = SimpleDocTemplate(
        str(output_path),
        pageSize=A4,
        rightMargin=PAGE_MARGIN,
        leftMargin=PAGE_MARGIN,
        topMargin=PAGE_MARGIN,
        bottomMargin=PAGE_MARGIN,
    )
    
    styles = getSampleStyleSheet()
    elements = []
    
    # Title
    elements.append(Paragraph("Submission", styles["Title"]))
    elements.append(Spacer(1, 20))
    
    # Infos client
    client_style = ParagraphStyle(
        "ClientInfo",
        parent=styles["BodyText"],
        alignment=TA_RIGHT,
    )

    client_name = escape(submission.get_client_name())
    submission_date = date.today().strftime("%d/%m/%Y")

    elements.append(
        Paragraph(
            f"To : {client_name}<br/>Created at : {submission_date}",
            client_style,
        )
    )
    elements.append(Spacer(1, 20))
    # Tableau facture
    rows = [["Code", "Product", "Quantity", "Unit price", "Total"]]
    for line in submission.lines:
        rows.append([
            line.product.code,
            line.product.name,
            str(line.quantity),
            f"{line.product.price} $",
            f"{line.get_subtotal()} $"
        ])
    
    table = Table(rows)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ("ALIGN", (0, 0), (-1, -1), "CENTER")
    ]))
    
    elements.append(table)
    elements.append(Spacer(1, 20))
    
    # Totals
    elements.append(Paragraph(f"Subtotal : {submission.get_subtotal()} $", styles["BodyText"]))
    
    for label, tax in submission.get_taxes_totals().items():
        elements.append(Paragraph(f"{label} : {tax} $", styles["BodyText"]))
    elements.append(Spacer(1, 20))
    elements.append(Paragraph(f"Total : {submission.get_total()} $", styles["BodyText"]))
    
    doc.build(elements)
    
