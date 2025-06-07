# export_note.py

from datetime import datetime
from weasyprint import HTML, CSS
from jinja2 import Template
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

def generate_soap_note_pdf(data):
    html_template = """
    <html>
    <head>
        <style>
            body { font-family: 'Helvetica', sans-serif; margin: 2cm; }
            h1, h2, h3 { color: #333; }
            .header { text-align: left; font-weight: bold; font-size: 14pt; margin-bottom: 10px; }
            .subheader { font-size: 10pt; margin-bottom: 5px; }
            .section-title { font-weight: bold; font-size: 12pt; margin-top: 20px; margin-bottom: 10px; }
            .field { margin-bottom: 5px; }
            .label { font-weight: bold; }
            table { width: 100%; border-collapse: collapse; margin-top: 10px; }
            th, td { border: 1px solid #444; padding: 6px; font-size: 10pt; text-align: center; }
            .footer { margin-top: 40px; display: flex; justify-content: space-between; font-size: 10pt; }
        </style>
    </head>
    <body>
        <div class="header">Dr. XXXXX XXXXXX</div>
        <div class="subheader">MD, RUGHS, FELLOW</div>
        <div class="subheader">Timings</div>

        <div class="section-title">Patient Details</div>
        {% for label, value in details %}
            <div class="field"><span class="label">{{ label }}:</span> {{ value }}</div>
        {% endfor %}

        <div class="section-title">Symptoms</div>
        <div class="field">{{ symptoms }}</div>

        <div class="section-title">Diagnosis</div>
        <div class="field">{{ primary_dx }}</div>
        <div class="field">{{ secondary_dx }}</div>

        <div class="section-title">Prescription</div>
        <table>
            <tr>
                <th>Drug</th>
                <th>BF/AF</th>
                <th>Morning</th>
                <th>Afternoon</th>
                <th>Night</th>
                <th>Total Quantity</th>
            </tr>
            {% for drug in prescribed_drugs %}
            <tr>
                <td>{{ drug }}</td>
                <td>{{ bfaf.get(drug, '') }}</td>
                <td>{{ schedule.get(drug, ['', '', ''])[0] }}</td>
                <td>{{ schedule.get(drug, ['', '', ''])[1] }}</td>
                <td>{{ schedule.get(drug, ['', '', ''])[2] }}</td>
                <td>{{ quantity.get(drug, '') }}</td>
            </tr>
            {% endfor %}
        </table>

        <div class="section-title">Prognosis</div>
        <div class="field">{{ prognosis }}</div>

        <div class="footer">
            <div>{{ today }}</div>
            <div>&lt;&lt;Place&gt;&gt;</div>
            <div>Electronic Signature of Doctor</div>
        </div>
    </body>
    </html>
    """

    template = Template(html_template)

    rendered_html = template.render(
        details=[
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
        ],
        symptoms=data.get("symptoms", ""),
        primary_dx=f"{data.get('primary_dx', '')} (ICD-10: {data.get('icd_code', '')})",
        secondary_dx=data.get("secondary_dx", ""),
        prescribed_drugs=data.get("prescribed_drugs", []),
        bfaf=data.get("bfaf", {}),
        schedule=data.get("dosage_schedule", {}),
        quantity=data.get("quantity", {}),
        prognosis=data.get("prognosis", ""),
        today=datetime.today().strftime("%d-%m-%Y")
    )

    output_path = "/mnt/data/soap_note_weasyprint.pdf"
    HTML(string=rendered_html).write_pdf(output_path)

    return output_path
