import streamlit as st
import pandas as pd
import os
import csv
from datetime import datetime

# Data loading functions
def load_data():
    data = {
        'reports': [],
        'votes': {},
        'testimonials': {}
    }

    if os.path.exists('reports.csv'):
        with open('reports.csv', 'r') as f:
            reader = csv.DictReader(f)
            data['reports'] = list(reader)

    if os.path.exists('votes.csv'):
        with open('votes.csv', 'r') as f:
            reader = csv.DictReader(f)
            data['votes'] = {row['report_id']: True for row in reader}

    if os.path.exists('testimonials.csv'):
        with open('testimonials.csv', 'r') as f:
            reader = csv.DictReader(f)
            data['testimonials'] = {row['report_id']: row['testimonial'] for row in reader}

    return data

def save_reports(reports):
    if reports:
        with open('reports.csv', 'w') as f:
            writer = csv.DictWriter(f, fieldnames=reports[0].keys())
            writer.writeheader()
            writer.writerows(reports)

# Categories and severity levels
CATEGORIES = [
    "Road Damage", "Streetlight Issue", "Garbage", "Water Leakage",
    "Sewage Problem", "Public Safety", "Noise Pollution", "Other"
]

SEVERITY_LEVELS = {
    "Mild": "🟢 Low impact",
    "Moderate": "🟡 Needs attention",
    "Severe": "🔴 Critical issue"
}

# Custom styling for government portal
def set_gov_style():
    st.markdown("""
    <style>
    .government-header {
        background-color: #2c3e50;
        color: white;
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 20px;
    }
    .report-card {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .priority-high {
        background-color: #ffdddd;
        border-left: 4px solid #ff5252;
    }
    .priority-medium {
        background-color: #fff8dd;
        border-left: 4px solid #ffd600;
    }
    .priority-low {
        background-color: #ddffdd;
        border-left: 4px solid #4caf50;
    }
    .status-pending {
        color: #ff9800;
        font-weight: bold;
    }
    .status-inprogress {
        color: #2196f3;
        font-weight: bold;
    }
    .status-resolved {
        color: #4caf50;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

def main():
    st.set_page_config(
        page_title="Government Portal", 
        page_icon="🏛", 
        layout="wide",
        initial_sidebar_state="expanded"
    )
    set_gov_style()

    st.markdown("""
    <div class="government-header">
        <h1 style="color:white; margin:0;">🏛 Government Portal</h1>
        <p style="color:white; margin:0;">Community Issue Management System</p>
    </div>
    """, unsafe_allow_html=True)

    st.sidebar.markdown("### Navigation")
    page = st.sidebar.radio("Go to", ["Issue Dashboard"])

    data = load_data()

    if page == "Issue Dashboard":
        show_issue_dashboard(data)

# You can implement show_voter_analytics and show_system_settings as before

def show_issue_dashboard(data):
    st.markdown("## 🏆 Priority Issues Leaderboard")

    col1, col2, col3 = st.columns(3)
    with col1:
        category_filter = st.selectbox("Filter by Category", ["All"] + CATEGORIES)
    with col2:
        status_filter = st.selectbox("Filter by Status", ["All", "Pending", "In Progress", "Resolved"])
    with col3:
        severity_filter = st.selectbox("Filter by Severity", ["All", "Mild", "Moderate", "Severe"])

    filtered_reports = data['reports'].copy()
    if category_filter != "All":
        filtered_reports = [r for r in filtered_reports if r['category'] == category_filter]
    if status_filter != "All":
        filtered_reports = [r for r in filtered_reports if r['status'] == status_filter]
    if severity_filter != "All":
        filtered_reports = [r for r in filtered_reports if r['severity'] == severity_filter]

    for report in filtered_reports:
        report['votes'] = int(report['votes'])
    filtered_reports.sort(key=lambda x: x['votes'], reverse=True)

    if not filtered_reports:
        st.info("No issues match the selected filters")
    else:
        df = pd.DataFrame(filtered_reports)
        df['Rank'] = range(1, len(df) + 1)
        df['Severity'] = df['severity'].map(SEVERITY_LEVELS)
        df['status'] = df['status'].apply(
            lambda x: f"<span class='status-{x.lower().replace(' ', '')}'>{x}</span>"
        )

        edited_df = st.data_editor(
            df[['Rank', 'problem_name', 'category', 'Severity', 'votes', 'status', 'location', 'timestamp']],
            column_config={
                "Rank": st.column_config.NumberColumn("Rank", width="small"),
                "problem_name": "Issue",
                "category": "Category",
                "Severity": "Severity",
                "votes": "Votes",
                "status": st.column_config.SelectboxColumn(
                    "Status",
                    options=["Pending", "In Progress", "Resolved"],
                    required=True
                ),
                "location": "Location",
                "timestamp": "Reported On"
            },
            hide_index=True,
            use_container_width=True,
            key="issues_editor"
        )

        if not edited_df.equals(df[['Rank', 'problem_name', 'category', 'Severity', 'votes', 'status', 'location', 'timestamp']]):
            for idx, row in edited_df.iterrows():
                report_id = filtered_reports[idx]['id']
                for report in data['reports']:
                    if report['id'] == report_id:
                        new_status = row['status'].split("'>")[1].split("<")[0]
                        if report['status'] != new_status:
                            report['status'] = new_status
                            st.success(f"Updated status for {report['problem_name']}")
            save_reports(data['reports'])

    st.markdown("## 📋 Detailed Reports")
    if not filtered_reports:
        st.info("No reports to display")
    else:
        for report in filtered_reports:
            priority_class = ""
            if report['severity'] == "Severe":
                priority_class = "priority-high"
            elif report['severity'] == "Moderate":
                priority_class = "priority-medium"
            else:
                priority_class = "priority-low"

            with st.expander(f"{report['problem_name']} - {report['votes']} votes", expanded=False):
                st.markdown(f"""
                <div class="report-card {priority_class}">
                    <div style="display: flex; justify-content: space-between;">
                        <div>
                            <strong>Category:</strong> {report['category']}<br>
                            <strong>Severity:</strong> {SEVERITY_LEVELS[report['severity']]}<br>
                            <strong>Location:</strong> {report['location']}<br>
                            <strong>Reporter:</strong> {report['reporter']}<br>
                        </div>
                        <div>
                            <strong>Status:</strong> <span class='status-{report['status'].lower().replace(' ', '')}'>{report['status']}</span><br>
                            <strong>Reported On:</strong> {report['timestamp']}<br>
                            <strong>Votes:</strong> {report['votes']}<br>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)


if _name_ == "_main_":
    main()
