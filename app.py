import streamlit as st
from auth.auth0_handler import login
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from leads.lead_manager import calculate_lead_score, assign_lead_tier
from leads.kanban import render_kanban
from leads.kanban import interactive_kanban


import os
st.set_page_config(page_title="NeuroCRM", layout="wide")
st.title("🧠 NeuroCRM – AI CRM for Freelancers")

user = login()
user_email = user.get("email", "unknown")
st.sidebar.success(f"Logged in as {user_email}")

from auth.auth0_handler import logout_button
logout_button()


# Unified Navigation
page = st.sidebar.radio("📂 Navigate", [
    "📋 Lead Tracker", "📝 Proposal Builder", "📊 Project Dashboard", 
    "📁 Saved Jobs", "📦 Exports", "⚙️ Settings"])

if page == "📋 Lead Tracker":
        st.subheader("📋 Manage Your Leads")

        df = init_leads_data(user_email)

        # 🎯 Add Lead Score & Priority
        df["Lead Score"] = df.apply(calculate_lead_score, axis=1)
        df["Priority"] = df["Lead Score"].apply(assign_lead_tier)

        # ✏️ Inline editing
        st.markdown("### ✏️ Edit Leads Inline")
        from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
        gb = GridOptionsBuilder.from_dataframe(df)
        gb.configure_default_column(editable=True)
        gb.configure_column("Lead Score", editable=False)
        gb.configure_column("Priority", editable=False)
        grid_options = gb.build()

        grid_response = AgGrid(
            df,
            gridOptions=grid_options,
            update_mode=GridUpdateMode.MODEL_CHANGED,
            fit_columns_on_grid_load=True
        )
        edited_df = grid_response["data"]

        if st.button("💾 Save Edits"):
            save_leads_data(user_email, edited_df)
            st.success("Leads updated successfully.")

        # ➕ Add New Lead
        st.markdown("### ➕ Add New Lead")
        with st.form("add_lead_form"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Name")
                email = st.text_input("Email")
                domain = st.selectbox("Project Type", ["Healthcare", "Finance", "E-commerce", "SaaS", "Other"])
                status = st.selectbox("Status", ["New", "Contacted", "Proposal Sent", "In Negotiation", "Won", "Lost"])
                budget = st.number_input("Budget ($)", min_value=0, step=500)
                resources = st.number_input("Resources", min_value=0, step=1)
            with col2:
                start_date = st.date_input("Start Date")
                end_date = st.date_input("End Date")
                notes = st.text_area("Notes")
                requirements = st.text_area("Customer Requirements")
                uploaded_file = st.file_uploader("Attach Project File")

            submitted = st.form_submit_button("Add Lead")
            if submitted:
                new_lead = pd.DataFrame([{
                    "Name": name, "Email": email, "Project Type": domain, "Status": status,
                    "Notes": notes, "Start Date": start_date, "End Date": end_date,
                    "Budget": budget, "Resources": resources,
                    "Customer Requirements": requirements
                }])
                df = pd.concat([df, new_lead], ignore_index=True)
                save_leads_data(user_email, df)

                if uploaded_file:
                    folder = f"data/uploads/{user_email}/{name.replace(' ', '_')}/"
                    os.makedirs(folder, exist_ok=True)
                    with open(os.path.join(folder, uploaded_file.name), "wb") as f:
                        f.write(uploaded_file.read())

                st.success("✅ Lead added successfully.")
                st.rerun()

        # 🗑️ Delete Lead
        st.markdown("### 🗑️ Delete a Lead")
        if len(df) == 0:
            st.info("No leads to delete.")
        else:
            lead_to_delete = st.selectbox("Select lead", [f"{i} - {row['Name']}" for i, row in df.iterrows()])
            if lead_to_delete:
                idx = int(lead_to_delete.split(" - ")[0])
                if st.button("🗑️ Confirm Delete"):
                    delete_lead(user_email, idx)
                    st.success("Deleted successfully.")
                    st.rerun()

        # 🔥 Summary Table
        st.markdown("### 🔥 Prioritized Lead Summary")
        st.dataframe(df[[
            "Name", "Email", "Project Type", "Status",
            "Budget", "End Date", "Lead Score", "Priority"
        ]])

        # 🧩 Interactive Kanban (with editing + auto-archive)
        st.markdown("### 🧱 Kanban View")
        interactive_kanban(df, user_email, save_leads_data)

elif page == "📝 Proposal Builder":
    from proposals.proposal_generator import generate_proposal_from_template
    from leads.lead_manager import init_leads_data

    st.header("📝 Proposal Generator")

    df = init_leads_data(user_email)

    if df.empty:
        st.warning("No projects found. Please add leads first.")
    else:
        st.markdown("### Select a Project")
        selected_name = st.selectbox("Project", df["Name"])
        selected_row = df[df["Name"] == selected_name].iloc[0]
        project_type = selected_row.get("Project Type", "General")

        st.markdown(f"**Detected Type:** `{project_type}`")
        brief = st.text_area("✍️ Client Brief", placeholder="What are the goals, challenges, scope, expectations?", height=150)

        if st.button("Generate Proposal"):
            if not brief.strip():
                st.warning("Please enter a client brief.")
            else:
                proposal = generate_proposal_from_template(selected_name, project_type, brief)
                st.success("✅ Proposal generated!")
                st.text_area("📄 Proposal Output", proposal, height=400)

elif page == "📊 Project Dashboard":
    from tracker.gantt import render_gantt
    from tracker.risk_analytics import analyze_risks
    from leads.lead_manager import init_leads_data

    st.header("📊 Project Dashboard")

    df = init_leads_data(user_email)
    if df.empty:
        st.warning("No leads found.")
    else:
        st.subheader("📅 Gantt Chart")
        render_gantt(df)

        st.subheader("🚨 Risk Insights")
        risks = analyze_risks(df)
        if risks:
            for r in risks:
                st.warning(r)
        else:
            st.success("✅ No critical risks detected.")

        st.subheader("📌 Work Breakdown Structure")
        from tracker.wbs import load_wbs, save_wbs, delete_milestone
        import plotly.express as px

        st.subheader("📌 Work Breakdown Structure")

        project_names = df["Name"].unique().tolist()
        selected_project = st.selectbox("Select Project for WBS", project_names)

        wbs_df = load_wbs(user_email, selected_project)

        # Add new milestone
        with st.expander("➕ Add New Milestone"):
            with st.form("milestone_form"):
                m_name = st.text_input("Milestone Name")
                m_status = st.selectbox("Status", ["Planned", "In Progress", "Completed"])
                m_due = st.date_input("Due Date")
                m_notes = st.text_area("Notes (optional)")
                if st.form_submit_button("Add"):
                    new_row = pd.DataFrame([{
                        "Milestone": m_name, "Status": m_status,
                        "Due Date": m_due, "Notes": m_notes
                    }])
                    wbs_df = pd.concat([wbs_df, new_row], ignore_index=True)
                    save_wbs(user_email, selected_project, wbs_df)
                    st.success("Milestone added!")
                    st.rerun()

        # Editable table
        st.markdown("### 📝 Existing Milestones")
        if wbs_df.empty:
            st.info("No milestones yet.")
        else:
            for i, row in wbs_df.iterrows():
                with st.expander(f"{row['Milestone']}"):
                    cols = st.columns([3, 1])
                    with cols[0]:
                        new_status = st.selectbox("Status", ["Planned", "In Progress", "Completed"], index=["Planned", "In Progress", "Completed"].index(row["Status"]), key=f"status_{i}")
                        new_notes = st.text_area("Notes", value=row["Notes"], key=f"notes_{i}")
                    with cols[1]:
                        if st.button("🗑 Delete", key=f"delete_{i}"):
                            delete_milestone(user_email, selected_project, i)
                            st.rerun()
                    # Save updated
                    wbs_df.at[i, "Status"] = new_status
                    wbs_df.at[i, "Notes"] = new_notes
            save_wbs(user_email, selected_project, wbs_df)

        # Optional Visualization
        st.markdown("### 📈 Timeline View")
        if not wbs_df.empty:
            try:
                plot_df = wbs_df.copy()
                plot_df["Due Date"] = pd.to_datetime(plot_df["Due Date"])
                fig = px.timeline(
                    plot_df,
                    x_start="Due Date",
                    x_end="Due Date",
                    y="Milestone",
                    color="Status",
                    hover_data=["Notes"]
                )
                fig.update_layout(height=400, title="WBS Timeline (Milestones Due)")
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.warning("Unable to render timeline: " + str(e))

elif page == "📁 Saved Jobs":
    from jobs.saved_jobs import load_saved_jobs, save_jobs, delete_job, add_job

    st.header("📁 Saved Freelance Jobs")

    df = load_saved_jobs(user_email)

    with st.expander("➕ Manually Add a Job"):
        with st.form("add_job_form"):
            title = st.text_input("Job Title")
            link = st.text_input("Job Link")
            summary = st.text_area("Summary", height=100)
            tags = st.text_input("Tags (comma-separated)")
            submitted = st.form_submit_button("Save Job")
            if submitted and title and link:
                add_job(user_email, title, link, summary, tags)
                st.success("✅ Job added")
                st.rerun()

    if df.empty:
        st.info("No saved jobs yet.")
    else:
        for i, row in df.iterrows():
            st.markdown(f"### [{row['Title']}]({row['Link']})")
            st.write(row['Summary'])

            cols = st.columns([3, 1, 1])
            with cols[0]:
                new_tags = st.text_input(f"Tags for job {i}", row["Tags"], key=f"tags_{i}")
            with cols[1]:
                applied = st.checkbox("✅ Applied", value=row["Applied"], key=f"applied_{i}")
            with cols[2]:
                if st.button("🗑 Delete", key=f"delete_{i}"):
                    delete_job(user_email, i)
                    st.success("Deleted.")
                    st.rerun()

            df.at[i, "Tags"] = new_tags
            df.at[i, "Applied"] = applied
            st.markdown("---")

        save_jobs(user_email, df)

elif page == "📦 Exports":
    from leads.lead_manager import init_leads_data
    from jobs.saved_jobs import load_saved_jobs
    from utils.export_tools import export_csv, export_excel

    st.header("📦 Export Center")

    # Export Leads
    st.subheader("📋 Export Leads")
    lead_df = init_leads_data(user_email)

    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            "⬇️ Download as CSV",
            export_csv(lead_df),
            file_name="leads.csv",
            mime="text/csv"
        )

    with col2:
        st.download_button(
            "⬇️ Download as Excel",
            export_excel(lead_df),
            file_name="leads.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    # Export Jobs
    st.subheader("📁 Export Saved Jobs")
    job_df = load_saved_jobs(user_email)

    col3, col4 = st.columns(2)
    with col3:
        st.download_button(
            "⬇️ Jobs as CSV",
            export_csv(job_df),
            file_name="saved_jobs.csv",
            mime="text/csv"
        )

    with col4:
        st.download_button(
            "⬇️ Jobs as Excel",
            export_excel(job_df),
            file_name="saved_jobs.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    # Placeholder for PDF/Reports
    st.subheader("🖨️ PDF / Full Report")
    st.info("PDF export will be available in the Pro version.")

elif page == "⚙️ Settings":
    st.header("⚙️ User Settings")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🧑 User Info")
        st.write(f"**Email:** {user.get('email', 'unknown')}")
        st.write(f"**Name:** {user.get('name', 'N/A')}")
        st.write(f"**Auth Provider:** {user.get('sub', 'N/A')}")

    with col2:
        st.subheader("🎛 Preferences")
        theme = st.radio("Theme", ["Light", "Dark (coming soon)"], index=0, disabled=True)
        lang = st.selectbox("Language", ["English", "Coming soon..."], index=0)

    st.markdown("### 🔄 Account Controls")
    st.info("🚧 Account deletion, notifications and billing coming soon.")
