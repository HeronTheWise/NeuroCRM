from jinja2 import Template
import pdfkit
from datetime import datetime

def generate_soap_note_pdf(data):
    html_template = """
    <html>
    <head>
    <style>
    body { font-family: sans-serif; padding: 2em; }
    h2 { color: #2c3e50; }
    .section { margin: 1em 0; }
    table { width: 100%; border-collapse: collapse; margin-top: 10px; }
    th, td { border: 1px solid #999; padding: 5px; text-align: left; font-size: 0.9em; }
    </style>
    </head>
    <body>
        <h2>SOAP Note</h2>
        <div class="section"><b>Patient Name:</b> {{ patient_name }}</div>
        <div class="section"><b>Age:</b> {{ age }} | <b>Gender:</b> {{ gender }}</div>
        <div class="section"><b>Visit Date:</b> {{ visit_date }}</div>
        <div class="section"><b>Chief Complaint:</b> {{ chief_complaint }}</div>
        <div class="section"><b>Symptoms:</b><br>{{ symptoms }}</div>
        <div class="section"><b>Diagnosis:</b><br>
            <ul>
                <li><b>Primary:</b> {{ primary_dx }} (ICD-10: {{ icd_code }})</li>
                <li><b>Secondary:</b> {{ secondary_dx }}</li>
            </ul>
        </div>
        <div class="section"><b>Prescription:</b>
            <table>
                <tr><th>Drug</th><th>BF/AF</th><th>Morning</th><th>Afternoon</th><th>Night</th><th>Qty</th></tr>
                {% for drug in prescribed_drugs %}
                <tr>
                    <td>{{ drug }}</td>
                    <td>{{ bfaf.get(drug, "") }}</td>
                    <td>{{ dosage_schedule.get(drug, ["", "", ""])[0] }}</td>
                    <td>{{ dosage_schedule.get(drug, ["", "", ""])[1] }}</td>
                    <td>{{ dosage_schedule.get(drug, ["", "", ""])[2] }}</td>
                    <td>{{ quantity.get(drug, "") }}</td>
                </tr>
                {% endfor %}
            </table>
        </div>
        <div class="section"><b>Prognosis:</b><br>{{ prognosis }}</div>
        <div class="section">Doctor: {{ doctor_name }} | Date: {{ today }}</div>
    </body>
    </html>
    """

    template = Template(html_template)
    html = template.render(
        patient_name=data.get("patient_name", ""),
        age=data.get("age", ""),
        gender=data.get("gender", ""),
        visit_date=data.get("visit_date", ""),
        chief_complaint=data.get("chief_complaint", ""),
        symptoms=data.get("symptoms", ""),
        primary_dx=data.get("primary_dx", ""),
        icd_code=data.get("icd_code", ""),
        secondary_dx=data.get("secondary_dx", ""),
        prescribed_drugs=data.get("prescribed_drugs", []),
        bfaf=data.get("bfaf", {}),
        dosage_schedule=data.get("dosage_schedule", {}),
        quantity=data.get("quantity", {}),
        prognosis=data.get("prognosis", ""),
        doctor_name=data.get("doctor_name", ""),
        today=datetime.today().strftime("%d-%m-%Y")
    )

    pdf_path = "/tmp/soap_note_output.pdf"
    pdfkit.from_string(html, pdf_path)
    return pdf_path
