from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.utils import simpleSplit
from datetime import datetime
from io import BytesIO
import os

def format_date(date_val):
    if isinstance(date_val, str):
        for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%Y/%m/%d"):
            try:
                return datetime.strptime(date_val, fmt).strftime("%d-%m-%Y")
            except ValueError:
                continue
        return date_val
    elif isinstance(date_val, datetime):
        return date_val.strftime("%d-%m-%Y")
    return ""

def wrap_text(text, font, size, max_width, canvas_obj):
    if not text:
        text = ""
    elif isinstance(text, bytes):
        text = text.decode('utf-8', errors='replace')
    elif not isinstance(text, str):
        text = str(text)
    return simpleSplit(text, font, size, max_width)

def generate_soap_note_pdf(data):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    y = height - 2 * cm

    def draw_wrapped_line(x, y, text, max_width, font="Helvetica", size=10, leading=12):
        c.setFont(font, size)
        lines = wrap_text(text, font, size, max_width, c)
        for line in lines:
            if y < 3 * cm:
                c.showPage()
                y = height - 2 * cm
                c.setFont(font, size)
            c.drawString(x, y, line)
            y -= leading
        return y

    # Header
    c.setFont("Helvetica-Bold", 12)
    c.drawString(2 * cm, y, "Dr. XXXXX XXXXXX")
    y -= 0.5 * cm
    c.setFont("Helvetica", 10)
    c.drawString(2 * cm, y, "MD, RUGHS, FELLOW")
    y -= 0.5 * cm
    c.drawString(2 * cm, y, "Timings")
    y -= 1 * cm

    # Title
    c.setFont("Helvetica-Bold", 12)
    c.drawString(2 * cm, y, "Patient Details")
    y -= 0.7 * cm

    # Patient Info
    details = [
        ("Name", data.get("patient_name", "")),
        ("Age", data.get("age", "")),
        ("Sex", data.get("gender", "")),
        ("Patient ID", data.get("patient_id", "")),
        ("Visit Date", format_date(data.get("visit_date", ""))),
        ("Contact", data.get("contact", "")),
        ("Doctor Name", data.get("doctor_name", "")),
        ("Clinic Name", data.get("clinic_name", "")),
        ("Referred By", data.get("referred_by", "")),
        ("Chief Complaint", data.get("chief_complaint", "")),
        ("Duration of Complaint", data.get("duration", ""))
    ]

    for label, value in details:
        y = draw_wrapped_line(2 * cm, y, f"{label}: {value}", width - 4 * cm)

    # Section: Symptoms
    y -= 0.7 * cm
    c.setFont("Helvetica-Bold", 10)
    c.drawString(2 * cm, y, "Symptoms")
    y -= 0.5 * cm
    y = draw_wrapped_line(2 * cm, y, data.get("symptoms", ""), width - 4 * cm)

    # Section: Diagnosis
    y -= 1 * cm
    c.setFont("Helvetica-Bold", 10)
    c.drawString(2 * cm, y, "Diagnosis")
    y -= 0.5 * cm
    primary_dx = f"{data.get('primary_dx', '')} (ICD-10: {data.get('icd_code', '')})"
    y = draw_wrapped_line(2 * cm, y, primary_dx, width - 4 * cm)
    y = draw_wrapped_line(2 * cm, y, data.get("secondary_dx", ""), width - 4 * cm)

    # Prescription Table
    y -= 1 * cm
    c.setFont("Helvetica-Bold", 10)
    c.drawString(2 * cm, y, "Prescription")
    y -= 0.5 * cm

    headers = ["Drug", "BF/AF", "Morning", "Afternoon", "Night", "Total Quantity"]
    col_x = [2 * cm, 6 * cm, 8 * cm, 10 * cm, 12 * cm, 14 * cm]
    c.setFont("Helvetica-Bold", 9)
    for i, h in enumerate(headers):
        c.drawString(col_x[i], y, h)
    y -= 0.5 * cm

    c.setFont("Helvetica", 9)
    for drug in data.get("prescribed_drugs", []):
        if y < 3 * cm:
            c.showPage()
            y = height - 2 * cm
            c.setFont("Helvetica", 9)
        c.drawString(col_x[0], y, str(drug))
        c.drawString(col_x[1], y, data.get("bfaf", {}).get(drug, ""))
        schedule = data.get("dosage_schedule", {}).get(drug, ["", "", ""])
        for i in range(3):
            c.drawString(col_x[2 + i], y, schedule[i] if i < len(schedule) else "")
        c.drawString(col_x[5], y, data.get("quantity", {}).get(drug, ""))
        y -= 0.5 * cm

    # Prognosis
    y -= 1 * cm
    c.setFont("Helvetica-Bold", 10)
    c.drawString(2 * cm, y, "Prognosis")
    y -= 0.5 * cm
    c.setFont("Helvetica", 10)
    y = draw_wrapped_line(2 * cm, y, data.get("prognosis", ""), width - 4 * cm)

    # Footer
    y = 2.5 * cm
    c.setFont("Helvetica", 10)
    c.drawString(2 * cm, y, datetime.today().strftime("%d-%m-%Y"))
    c.drawString(6 * cm, y, "<<Place>>")
    c.drawRightString(width - 2 * cm, y, "Electronic Signature of Doctor")

    # Finalize PDF and save
    c.save()
    buffer.seek(0)

    # Define path
    output_path = "/mnt/data/soap_note_output.pdf"
    dir_path = os.path.dirname(output_path)

    # Ensure directory exists and is valid
    if dir_path and not os.path.exists(dir_path):
        try:
            os.makedirs(dir_path, exist_ok=True)
        except Exception as e:
            raise RuntimeError(f"Could not create directory '{dir_path}': {e}")

    # Write file
    try:
        with open(output_path, "wb") as f:
            f.write(buffer.getvalue())
    except Exception as e:
        raise RuntimeError(f"Could not write PDF to '{output_path}': {e}")
    finally:
        buffer.close()

    return output_path

