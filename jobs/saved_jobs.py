import pandas as pd
import os

def get_job_path(user_email):
    safe_email = user_email.replace("@", "_at_").replace(".", "_dot_")
    return f"data/users/saved_jobs_{safe_email}.csv"

def load_saved_jobs(user_email):
    path = get_job_path(user_email)
    if not os.path.exists(path):
        return pd.DataFrame(columns=["Title", "Link", "Summary", "Tags", "Applied"])
    return pd.read_csv(path)

def save_jobs(user_email, df):
    df.to_csv(get_job_path(user_email), index=False)

def add_job(user_email, title, link, summary, tags=""):
    df = load_saved_jobs(user_email)
    new_job = {
        "Title": title,
        "Link": link,
        "Summary": summary,
        "Tags": tags,
        "Applied": False
    }
    df = pd.concat([df, pd.DataFrame([new_job])], ignore_index=True)
    save_jobs(user_email, df)

def delete_job(user_email, index):
    df = load_saved_jobs(user_email)
    df.drop(index, inplace=True)
    df.reset_index(drop=True, inplace=True)
    save_jobs(user_email, df)
