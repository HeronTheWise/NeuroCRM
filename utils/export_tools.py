import pandas as pd
import io

def export_csv(df):
    return df.to_csv(index=False).encode('utf-8')

def export_excel(df):
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    return buffer.getvalue()
