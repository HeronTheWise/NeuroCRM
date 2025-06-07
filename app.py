import streamlit as st
import pandas as pd
import os
from io import BytesIO
from utils.export_note import generate_soap_note_pdf

# Ensure upload folder exists
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Load data safely
try:
    icd_df = pd.read_csv("data/icd10.csv")
    drug_df = pd.read_csv("data/drug_list.csv")
    symptoms_list = pd.read_csv("data/symptoms_list.csv")["symptom"].tolist()
except FileNotFoundError as e:
    st.error(f"Missing data file: {e}")
    st.stop()

st.set_page_config(page_title="SOAP Note Builder", layout="centered")
st.title("Subjective, Objective, Assessment, Plan (SOAP)")

# Basic Details
st.header("Basic Details")
patient_name = st.text_input("Patient Name")
age = st.number_input("Age", min_value=0, max_value=120, value=30)
gender = st.selectbox("Gender", options=["Male", "Female", "Other"])
patient_id = st.text_input("Patient ID")
visit_date = st.date_input("Visit Date")
contact = st.text_input("Contact Information")
doctor_name = st.text_input("Doctor's Name")
clinic_name = st.text_input("Clinic Name")
referred_by = st.text_input("Referred By")

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

uploaded_file = st.file_uploader("Upload Lab Report (PDF, Image, etc.)", type=["pdf", "png", "jpg", "jpeg"])
if uploaded_file:
    file_path = os.path.join(UPLOAD_DIR, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.read())
    st.success(f"Uploaded to: {file_path}")
    lab_results = f"Attached file: {uploaded_file.name}"
else:
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

# Dosage timing
dosage_schedule = {}
if prescribed_drugs:
    st.subheader("Dosage Timing")
    for drug in prescribed_drugs:
        cols = st.columns(3)
        timing = {
            "Morning": cols[0].checkbox(f"{drug} - Morning"),
            "Afternoon": cols[1].checkbox(f"{drug} - Afternoon"),
            "Night": cols[2].checkbox(f"{drug} - Night")
        }
        dosage_schedule[drug] = [k for k, v in timing.items() if v]

if st.button("📝 Generate Note"):
    if not chief_complaint or not primary_dx:
        st.error("Please fill in at least Chief Complaint and Primary Diagnosis.")
    else:
        data = {
            "patient_name": patient_name,
            "age": age,
            "gender": gender,
            "patient_id": patient_id,
            "visit_date": str(visit_date),
            "contact": contact,
            "doctor_name": doctor_name,
            "clinic_name": clinic_name,
            "referred_by": referred_by,
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
            "dosage_schedule": dosage_schedule
        }

        pdf_output = generate_soap_note_pdf(data)  # We'll update this function next to handle new fields

        st.download_button(
            label="📥 Download SOAP Note (PDF)",
            data=pdf_output,
            file_name="soap_note.pdf",
            mime="application/pdf"
        )
        st.success("Note generated successfully!")
