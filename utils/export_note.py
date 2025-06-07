from fpdf import FPDF
from io import BytesIO
import os

def generate_soap_note_pdf(data, logo_path=None, watermark_text=None):
    """
    Generate a PDF bytes object of the SOAP note from data dictionary.
    
    Args:
        data (dict): Contains keys:
            - chief_complaint (str)
            - duration (str)
            - symptoms (list of str)
            - bp (str)
            - temp (str)
            - hr (str)
            - spo2 (str)
            - clinical_findings (str)
            - lab_results (str)
            - primary_dx (str)
            - icd_code (str)
            - secondary_dx (str)
            - treatment_plan (str)
            - prescribed_drugs (list of str)
        logo_path (str or None): Path to logo image to add on top (PNG/JPG).
        watermark_text (str or None): Text to use as a faint watermark.

    Returns:
        BytesIO: PDF file in memory.
    """
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Add logo if exists
    if logo_path and os.path.exists(logo_path):
        pdf.image(logo_path, x=10, y=8, w=33)
        pdf.ln(25)  # space after logo
    else:
        pdf.ln(15)
    
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "SOAP NOTE", ln=True, align='C')
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 5, "="*40, ln=True)
    pdf.ln(5)

    # Add watermark if specified (simple faded text)
    if watermark_text:
        pdf.set_text_color(200, 200, 200)
        pdf.set_font("Arial", 'B', 50)
        pdf.rotate(45, x=pdf.w / 2, y=pdf.h / 2)
        pdf.text(x=pdf.w / 4, y=pdf.h / 2, txt=watermark_text)
        pdf.rotate(0)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Arial", '', 12)

    # Write sections
    def write_section(title, content_lines):
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, title, ln=True)
        pdf.set_font("Arial", '', 12)
        for line in content_lines:
            pdf.multi_cell(0, 8, line)
        pdf.ln(5)

    subjective_lines = [
        f"- Chief Complaint: {data.get('chief_complaint', '')}",
        f"- Duration: {data.get('duration', '')}",
        f"- Symptoms: {', '.join(data.get('symptoms', []))}"
    ]

    objective_lines = [
        f"- BP: {data.get('bp', '')}, Temp: {data.get('temp', '')}, HR: {data.get('hr', '')}, SpO2: {data.get('spo2', '')}",
        f"- Clinical Findings: {data.get('clinical_findings', '')}",
        f"- Lab Results: {data.get('lab_results', '')}"
    ]

    assessment_lines = [
        f"- Primary Diagnosis: {data.get('primary_dx', '')} (ICD-10: {data.get('icd_code', '')})",
        f"- Secondary Diagnosis: {data.get('secondary_dx', '')}"
    ]

    plan_lines = [
        f"- Treatment: {data.get('treatment_plan', '')}",
        f"- Medications: {', '.join(data.get('prescribed_drugs', []))}"
    ]

    write_section("Subjective", subjective_lines)
    write_section("Objective", objective_lines)
    write_section("Assessment", assessment_lines)
    write_section("Plan", plan_lines)

    # Output to BytesIO
    pdf_output = BytesIO()
    pdf.output(pdf_output)
    pdf_output.seek(0)

    return pdf_output
