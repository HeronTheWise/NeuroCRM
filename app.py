import streamlit as st
import pandas as pd
from export_note import generate_soap_note_pdf  # assuming this file is in the same folder or installed
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

        # Generate PDF bytes with optional logo and watermark (remove or customize these args)
        pdf_output = generate_soap_note_pdf(
            data,
            logo_path="assets/logo.png",       # Optional: set None if no logo
            watermark_text=None                # Optional: e.g. "CONFIDENTIAL"
        )

        st.download_button(
            label="📥 Download SOAP Note (PDF)",
            data=pdf_output,
            file_name="soap_note.pdf",
            mime="application/pdf"
        )
        st.success("Note generated successfully!")
