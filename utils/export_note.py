from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from datetime import datetime
from io import BytesIO

def generate_soap_note_pdf(data):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Header Section
    c.setFont("Helvetica-Bold", 12)
    c.drawString(2*cm, height - 2*cm, "Dr. XXXXX XXXXXX")
    c.setFont("Helvetica", 10)
    c.drawString(2*cm, height - 2.5*cm, "MD, RUGHS, FELLOW")
    c.drawString(2*cm, height - 3*cm, "Timings")

    # Title Section
    c.setFont("Helvetica-Bold", 12)
    y = height - 4.2*cm
    c.drawString(2*cm, y, "Patient Details")
    y -= 0.5*cm

    # Basic Details Table
    details = [
        ("Name", data.get("patient_name", "")),
        ("Age", data.get("age", "")),
        ("Sex", data.get("gender", "")),
        ("Patient ID", data.get("patient_id", "")),
        ("Visit Date", data.get("visit_date", "").strftime("%d-%m-%Y")),
        ("Contact", data.get("contact", "")),
        ("Doctor Name", data.get("doctor_name", "")),
        ("Clinic Name", data.get("clinic_name", "")),
        ("Referred By", data.get("referred_by", "")),
        ("Chief Complaint", data.get("chief_complaint", "")),
        ("Duration of Complaint", data.get("duration", ""))
        ]
    c.setFont("Helvetica", 10)
    for label, value in details:
        c.drawString(2*cm, y, f"{label}: {value}")
        y -= 0.5*cm

    # Section: Symptoms
    y -= 0.5*cm
    c.setFont("Helvetica-Bold", 10)
    c.drawString(2*cm, y, "Symptoms")
    y -= 0.5*cm
    c.setFont("Helvetica", 10)
    c.drawString(2*cm, y, data.get("symptoms", ""))

    # Section: Diagnosis
    y -= 1*cm
    c.setFont("Helvetica-Bold", 10)
    c.drawString(2*cm, y, "Diagnosis")
    y -= 0.5*cm
    c.setFont("Helvetica", 10)
    dx_str = f"{data.get('primary_dx', '')} (ICD-10: {data.get('icd_code', '')})"
    c.drawString(2*cm, y, dx_str)
    y -= 0.5*cm
    c.drawString(2*cm, y, data.get("secondary_dx", ""))

    # Section: Prescription Table
    y -= 1*cm
    c.setFont("Helvetica-Bold", 10)
    c.drawString(2*cm, y, "Prescription")
    y -= 0.5*cm

    table_headers = ["Drug", "BF/AF", "Morning", "Afternoon", "Night", "Total Quantity"]
    col_x = [2*cm, 6*cm, 8*cm, 10*cm, 12*cm, 14*cm]
    for i, header in enumerate(table_headers):
        c.drawString(col_x[i], y, header)
    y -= 0.5*cm

    c.setFont("Helvetica", 9)
    for drug in data.get("prescribed_drugs", []):
        c.drawString(col_x[0], y, drug)
        c.drawString(col_x[1], y, data.get("bfaf", {}).get(drug, ""))
        schedule = data.get("dosage_schedule", {}).get(drug, ["", "", ""])
        for i in range(3):
            c.drawString(col_x[2+i], y, schedule[i] if i < len(schedule) else "")
        c.drawString(col_x[5], y, data.get("quantity", {}).get(drug, ""))
        y -= 0.5*cm

    # Prognosis
    y -= 1*cm
    c.setFont("Helvetica-Bold", 10)
    c.drawString(2*cm, y, "Prognosis")
    y -= 0.5*cm
    c.setFont("Helvetica", 10)
    c.drawString(2*cm, y, data.get("prognosis", ""))

    # Footer
    y = 2.5*cm
    c.setFont("Helvetica", 10)
    c.drawString(2*cm, y, datetime.today().strftime("%d-%m-%Y"))
    c.drawString(6*cm, y, "<<Place>>")
    c.drawRightString(width - 2*cm, y, "Electronic Signature of Doctor")

    c.save()
    buffer.seek(0)
    buffer_path = "/mnt/data/soap_note_output.pdf"
    with open(buffer_path, "wb") as f:
        f.write(buffer.getvalue())

    buffer.close()
    buffer_path

