# This script builds a SOAP Note form using Streamlit.
# To run it locally, make sure Streamlit is installed: `pip install streamlit`

try:
    import streamlit as st
except ModuleNotFoundError:
    raise ModuleNotFoundError("Streamlit is not installed. Please install it with 'pip install streamlit'.")

import pandas as pd
from io import BytesIO
from fpdf import FPDF

# Load data safely
try:
    icd_df = pd.read_csv("data/icd10.csv")
    drug_df = pd.read_csv("data/drug_list.csv")
    symptoms_list = pd.read_csv("data/symptoms_list.csv")["symptom"].tolist()
except FileNotFoundError as e:
    st.error(f"Missing data file: {e}")
    st.stop()

st.set_page_config(page_title="SOAP Note Builder", layout="centered")
st.title("🩺 Doctor's SOAP Note Builder (Lite)")

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

# Generate and export
if st.button("📝 Generate Note"):
    note = f"""
    SOAP NOTE
    =============

    Subjective:
    - Chief Complaint: {chief_complaint}
    - Duration: {duration}
    - Symptoms: {', '.join(symptoms)}

    Objective:
    - BP: {bp}, Temp: {temp}, HR: {hr}, SpO2: {spo2}
    - Clinical Findings: {clinical_findings}
    - Lab Results: {lab_results}

    Assessment:
    - Primary Diagnosis: {primary_dx} (ICD-10: {icd_code})
    - Secondary Diagnosis: {secondary_dx}

    Plan:
    - Treatment: {treatment_plan}
    - Medications: {', '.join(prescribed_drugs)}
    """

    # Generate PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for line in note.strip().split("\n"):
        pdf.multi_cell(0, 10, line)

    pdf_output = BytesIO()
    pdf.output(pdf_output)
    pdf_output.seek(0)

    st.download_button(
        label="📥 Download SOAP Note (PDF)",
        data=pdf_output,
        file_name="soap_note.pdf",
        mime="application/pdf"
    )

    st.success("Note generated successfully!")
