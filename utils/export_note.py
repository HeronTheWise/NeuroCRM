from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from datetime import datetime
from io import BytesIO

def generate_soap_note_pdf(data):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Watermark
    c.setFont("Helvetica", 40)
    c.setFillGray(0.9, 0.5)
    c.saveState()
    c.translate(10*cm, 15*cm)
    c.rotate(45)
    c.drawCentredString(0, 0, "NeuroCare Clinic")
    c.restoreState()

    # Header
    c.setFont("Helvetica-Bold", 16)
    c.setFillColorRGB(0, 0, 0)
    c.drawString(2*cm, height - 2*cm, "SOAP Note")

    c.setFont("Helvetica", 10)
    c.drawString(2*cm, height - 2.5*cm, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    y = height - 3.5*cm
    line_height = 14

    def write_line(label, value):
        nonlocal y
        if isinstance(value, list):
            value = ", ".join(value)
        text = f"{label}: {value}"
        for line in textwrap(text, 100):
            c.drawString(2*cm, y, line)
            y -= line_height

    def textwrap(text, width=100):
        import textwrap
        return textwrap.wrap(text, width)

    # Subjective
    c.setFont("Helvetica-Bold", 12)
    c.drawString(2*cm, y, "Subjective")
    y -= line_height
    c.setFont("Helvetica", 10)
    write_line("Chief Complaint", data["chief_complaint"])
    write_line("Duration", data["duration"])
    write_line("Symptoms", data["symptoms"])

    # Objective
    c.setFont("Helvetica-Bold", 12)
    c.drawString(2*cm, y, "Objective")
    y -= line_height
    c.setFont("Helvetica", 10)
    write_line("Blood Pressure", data["bp"])
    write_line("Temperature", data["temp"])
    write_line("Heart Rate", data["hr"])
    write_line("SpO2", data["spo2"])
    write_line("Clinical Findings", data["clinical_findings"])
    write_line("Lab Results", data["lab_results"])

    # Assessment
    c.setFont("Helvetica-Bold", 12)
    c.drawString(2*cm, y, "Assessment")
    y -= line_height
    c.setFont("Helvetica", 10)
    write_line("Primary Diagnosis", f"{data['primary_dx']} (ICD-10: {data['icd_code']})")
    write_line("Secondary Diagnosis", data["secondary_dx"])

    # Plan
    c.setFont("Helvetica-Bold", 12)
    c.drawString(2*cm, y, "Plan")
    y -= line_height
    c.setFont("Helvetica", 10)
    write_line("Treatment Plan", data["treatment_plan"])

    prescribed_drugs = data.get("prescribed_drugs", [])
    dosage_schedule = data.get("dosage_schedule", {})

    for drug in prescribed_drugs:
        dosage = ", ".join(dosage_schedule.get(drug, []))
        write_line("Medication", f"{drug} - ({dosage if dosage else 'No time specified'})")

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer.getvalue()
