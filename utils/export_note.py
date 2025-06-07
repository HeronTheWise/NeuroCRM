from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from io import BytesIO
import os

def generate_soap_note_pdf(note_text: str) -> BytesIO:
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    c.setFont("Helvetica", 11)

    margin = 50
    max_width = width - 2 * margin
    y = height - margin

    for line in note_text.strip().split('\n'):
        lines = split_text_to_fit(line, c, max_width)
        for subline in lines:
            if y < margin:
                c.showPage()
                c.setFont("Helvetica", 11)
                y = height - margin
            c.drawString(margin, y, subline)
            y -= 15

    c.save()
    buffer.seek(0)
    return buffer

def split_text_to_fit(text, canvas_obj, max_width):
    words = text.split()
    lines = []
    line = ""
    for word in words:
        test_line = line + (" " if line else "") + word
        if canvas_obj.stringWidth(test_line, "Helvetica", 11) < max_width:
            line = test_line
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines