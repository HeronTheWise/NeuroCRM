import pandas as pd
import os

def get_lead_path(user_email):
    safe_email = user_email.replace("@", "_at_").replace(".", "_dot_")
    return f"data/users/leads_{safe_email}.csv"

COLUMNS = [
    "Name", "Email", "Project Type", "Status", "Notes",
    "Start Date", "End Date", "Budget", "Resources", "Customer Requirements"
]

def init_leads_data(user_email):
    path = get_lead_path(user_email)
    if not os.path.exists(path):
        df = pd.DataFrame(columns=COLUMNS)
        df.to_csv(path, index=False)
    else:
        df = pd.read_csv(path)
        for col in COLUMNS:
            if col not in df.columns:
                df[col] = ""
    return df

def save_leads_data(user_email, df):
    path = get_lead_path(user_email)
    df.to_csv(path, index=False)

def delete_lead(user_email, index):
    df = init_leads_data(user_email)
    df.drop(index, inplace=True)
    df.reset_index(drop=True, inplace=True)
    save_leads_data(user_email, df)
