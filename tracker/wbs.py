import os
import pandas as pd

def get_wbs_path(user_email, project_name):
    safe_email = user_email.replace("@", "_at_").replace(".", "_dot_")
    folder = f"data/users/wbs_{safe_email}"
    os.makedirs(folder, exist_ok=True)
    return f"{folder}/{project_name.replace(' ', '_')}.csv"

def load_wbs(user_email, project_name):
    path = get_wbs_path(user_email, project_name)
    return pd.read_csv(path) if os.path.exists(path) else pd.DataFrame(columns=["Milestone", "Status", "Due Date", "Notes"])

def save_wbs(user_email, project_name, df):
    df.to_csv(get_wbs_path(user_email, project_name), index=False)

def delete_milestone(user_email, project_name, index):
    df = load_wbs(user_email, project_name)
    df.drop(index, inplace=True)
    df.reset_index(drop=True, inplace=True)
    save_wbs(user_email, project_name, df)
