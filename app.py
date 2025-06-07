import streamlit as st
import pandas as pd
from utils.export_note import generate_soap_note_pdf  # assuming this file is in the same folder or installed
from io import BytesIO

# Load data safely at app start
try:
    icd_df = pd.read_csv("data/icd10.csv")
    drug_df = pd.read_csv("data/drug_list.csv")
    symptoms_list = pd.read_csv("data/symptoms_list.csv")["symptom"].tolist()
except FileNotFoundError as e:
    st.error(f"Missing data file: {e}")
    st.stop()

st.set_page_config(page_title="SOAP Note Builder", layout="centered")
st.title("Subjective.Objective.Assessment.Plan Note")

# Subjective
st.header("1. Subjective")
chief_complaint = st.text_input("Chief Complaint")
duration = st.text_input("Duration of symptoms (e.g., 3 days, 1 week)")
symptoms = st.multiselect("Select symptoms", options=symptoms_list)

# Objective
st.header("2. Objective")
bp = st.text_input("Blood Pressure (e.g., 120/80 mmHg)")
temp = st.text_input("Temperature (°C)")
hr = st.text_input("Heart Rate (bpm)")
spo2 = st.text_input("SpO2 (%)")
clinical_findings = st.text_area("Clinical Findings")
lab_results = st.text_area("Lab Test Results")

# Assessment
st.header("3. Assessment")
primary_dx = st.selectbox("Primary Diagnosis", options=icd_df["diagnosis"].tolist())
icd_code = icd_df[icd_df["diagnosis"] == primary_dx]["code"].values[0]
secondary_dx = st.text_input("Secondary Diagnosis (optional)")

# Plan
st.header("4. Plan")
treatment_plan = st.text_area("Treatment Plan")
prescribed_drugs = st.multiselect("Prescribed Medications", options=drug_df["drug"].tolist())

note = "" 

if st.button("📝 Generate Note"):

    # Validate minimal inputs
    if not chief_complaint or not primary_dx:
        st.error("Please fill in at least Chief Complaint and Primary Diagnosis to generate the note.")
    else:
        data = {
            "chief_complaint": chief_complaint,
            "duration": duration,
            "symptoms": symptoms,
            "bp": bp,
            "temp": temp,
            "hr": hr,
            "spo2": spo2,
            "clinical_findings": clinical_findings,
            "lab_results": lab_results,
            "primary_dx": primary_dx,
            "icd_code": icd_code,
            "secondary_dx": secondary_dx,
            "treatment_plan": treatment_plan,
            "prescribed_drugs": prescribed_drugs,
        }

        # Build the note text from the data dict
        note = f"""
SOAP NOTE
==========

Subjective:
- Chief Complaint: {data['chief_complaint']}
- Duration: {data['duration']}
- Symptoms: {', '.join(data['symptoms']) if data['symptoms'] else 'N/A'}

Objective:
- BP: {data['bp']}, Temp: {data['temp']}, HR: {data['hr']}, SpO2: {data['spo2']}
- Clinical Findings: {data['clinical_findings']}
- Lab Results: {data['lab_results']}

Assessment:
- Primary Diagnosis: {data['primary_dx']} (ICD-10: {data['icd_code']})
- Secondary Diagnosis: {data['secondary_dx'] if data['secondary_dx'] else 'N/A'}

Plan:
- Treatment: {data['treatment_plan']}
- Medications: {', '.join(data['prescribed_drugs']) if data['prescribed_drugs'] else 'N/A'}
"""

        # Generate PDF bytes by passing the note string
        pdf_output = generate_soap_note_pdf(note)

        st.download_button(
            label="📥 Download SOAP Note (PDF)",
            data=pdf_output,
            file_name="soap_note.pdf",
            mime="application/pdf"
        )
        st.success("Note generated successfully!")
