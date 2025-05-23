import streamlit as st
from streamlit_sortables import sortables
import pandas as pd
import plotly.express as px
from streamlit_elements import elements, mui
import os

ARCHIVE_DIR = "data/archives"

def archive_leads(user_email, leads_df):
    os.makedirs(ARCHIVE_DIR, exist_ok=True)
    archive_path = f"{ARCHIVE_DIR}/archived_leads_{user_email.replace('@', '_')}.csv"
    if os.path.exists(archive_path):
        archived_df = pd.read_csv(archive_path)
    else:
        archived_df = pd.DataFrame(columns=leads_df.columns)

    archived_df = pd.concat([archived_df, leads_df], ignore_index=True)
    archived_df.to_csv(archive_path, index=False)

def interactive_kanban(df, user_email, save_fn):
    st.markdown("## 🗂️ Kanban Board with Drag-and-Drop + Editing")

    statuses = ["New", "Contacted", "Proposal Sent", "In Negotiation", "Won", "Lost"]
    status_columns = {status: [] for status in statuses}

    for i, row in df.iterrows():
        status_columns[row["Status"]].append(f"{row['Name']}#{i}")

    reordered = sortables(
        items=list(status_columns.values()),
        direction="horizontal",
        labels=statuses,
        key="kanban_drag"
    )

    new_df = df.copy()
    for col_index, column in enumerate(reordered):
        new_status = statuses[col_index]
        for item in column:
            name, index = item.split("#")
            index = int(index)
            new_df.at[index, "Status"] = new_status

    # Archive Won/Lost leads
    completed = new_df[new_df["Status"].isin(["Won", "Lost"])]
    if not completed.empty:
        archive_leads(user_email, completed)
        new_df = new_df[~new_df["Status"].isin(["Won", "Lost"])]
        st.info(f"📦 Archived {len(completed)} completed leads.")

    # Save changes
    if not new_df.equals(df):
        save_fn(user_email, new_df)
        st.success("✅ Lead statuses updated.")
        st.rerun()

    # Summary
    st.markdown("## 📊 Summary by Status")
    status_summary = new_df["Status"].value_counts().reset_index()
    status_summary.columns = ["Status", "Count"]
    fig = px.bar(status_summary, x="Status", y="Count", color="Status", title="Lead Count by Status")
    st.plotly_chart(fig, use_container_width=True)

    # Lead Cards (Editable)
    st.markdown("## 📝 Lead Cards (Editable)")
    with elements("kanban_cards"):
        for status in statuses:
            with mui.Paper(key=status, elevation=2, style={
                "padding": "1rem", "margin": "0.5rem", "width": "18rem",
                "display": "inline-block", "verticalAlign": "top"
            }):
                mui.Typography(status, variant="h6")
                cards = new_df[new_df["Status"] == status]
                for i, row in cards.iterrows():
                    with mui.Card(key=row["Name"], style={"marginTop": "0.5rem"}):
                        with mui.CardContent():
                            name = st.text_input(f"Name_{i}", row["Name"], key=f"name_{i}")
                            notes = st.text_area(f"Notes_{i}", row.get("Notes", ""), key=f"notes_{i}")
                            new_df.at[i, "Name"] = name
                            new_df.at[i, "Notes"] = notes

    # Update edited fields
    if st.button("💾 Save Edits"):
        save_fn(user_email, new_df)
        st.success("Leads updated.")
        st.rerun()
