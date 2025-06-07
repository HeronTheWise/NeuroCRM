# export_note.py

from fpdf import FPDF
from io import BytesIO

def generate_soap_note_pdf(data: dict) -> BytesIO:
    """
    Generates a PDF from the given SOAP note data dictionary.
    
    Args:
        data (dict): Dictionary containing SOAP note fields.

    Returns:
        BytesIO: PDF in memory, ready for download.
    """
    note = f"""
    SOAP NOTE
    =============

    Subjective:
    - Chief Complaint: {data.get('chief_complaint')}
    - Duration: {data.get('duration')}
    - Symptoms: {', '.join(data.get('symptoms', []))}

    Objective:
    - BP: {data.get('bp')}, Temp: {data.get('temp')}, HR: {data.get('hr')}, SpO2: {data.get('spo2')}
    - Clinical Findings: {data.get('clinical_findings')}
    - Lab Results: {data.get('lab_results')}

    Assessment:
    - Primary Diagnosis: {data.get('primary_dx')} (ICD-10: {data.get('icd_code')})
    - Secondary Diagnosis: {data.get('secondary_dx')}

    Plan:
    - Treatment: {data.get('treatment_plan')}
    - Medications: {', '.join(data.get('prescribed_drugs', []))}
    """

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    for line in note.strip().split("\n"):
        pdf.multi_cell(0, 10, line.strip())

    output = BytesIO()
    pdf.output(output)
    output.seek(0)
    return output
