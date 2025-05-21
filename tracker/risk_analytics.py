import pandas as pd

def analyze_risks(df):
    risks = []

    today = pd.Timestamp.today()
    df["Start Date"] = pd.to_datetime(df["Start Date"], errors='coerce')
    df["End Date"] = pd.to_datetime(df["End Date"], errors='coerce')

    for _, row in df.iterrows():
        if pd.notna(row["End Date"]) and row["End Date"] < today and row["Status"] != "Won":
            risks.append(f"⚠️ {row['Name']} is past due.")
        if row["Resources"] < 2 and row["Budget"] > 10000:
            risks.append(f"🛠 {row['Name']} may be under-resourced for budget ${row['Budget']}.")

    return risks
