import streamlit as st
import google.generativeai as genai
from PIL import Image
import time
import uuid
import json
from datetime import datetime
import pandas as pd
from streamlit_lottie import st_lottie
import requests
import os
import csv

# Configure Lottie
def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# Data persistence functions
def load_data():
    # Load reports
    if os.path.exists('reports.csv'):
        st.session_state.reports = []
        with open('reports.csv', 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Convert data types
                row['votes'] = int(row['votes'])
                st.session_state.reports.append(row)

    # Load votes
    if os.path.exists('votes.csv'):
        st.session_state.votes = {}
        with open('votes.csv', 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                st.session_state.votes[row['report_id']] = True

    # Load testimonials
    if os.path.exists('testimonials.csv'):
        st.session_state.testimonials = {}
        with open('testimonials.csv', 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                st.session_state.testimonials[row['report_id']] = row['testimonial']

    # Load wallet
    if os.path.exists('wallet.csv'):
        with open('wallet.csv', 'r') as f:
            reader = csv.DictReader(f)
            row = next(reader, None)
            if row:
                st.session_state.wallet_balance = int(row['balance'])

    # Load coupons
    if os.path.exists('available_coupons.csv'):
        st.session_state.available_coupons = {}
        with open('available_coupons.csv', 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                st.session_state.available_coupons[row['coupon']] = int(row['count'])

    if os.path.exists('redeemed_coupons.csv'):
        st.session_state.redeemed_coupons = {}
        with open('redeemed_coupons.csv', 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                st.session_state.redeemed_coupons[row['coupon']] = int(row['count'])

def save_reports():
    if 'reports' in st.session_state and st.session_state.reports:
        with open('reports.csv', 'w') as f:
            writer = csv.DictWriter(f, fieldnames=st.session_state.reports[0].keys())
            writer.writeheader()
            for report in st.session_state.reports:
                writer.writerow(report)

def save_votes():
    if 'votes' in st.session_state:
        with open('votes.csv', 'w') as f:
            writer = csv.DictWriter(f, fieldnames=['report_id'])
            writer.writeheader()
            for report_id in st.session_state.votes:
                writer.writerow({'report_id': report_id})

def save_testimonials():
    if 'testimonials' in st.session_state:
        with open('testimonials.csv', 'w') as f:
            writer = csv.DictWriter(f, fieldnames=['report_id', 'testimonial'])
            writer.writeheader()
            for report_id, testimonial in st.session_state.testimonials.items():
                writer.writerow({'report_id': report_id, 'testimonial': testimonial})

def save_wallet():
    if 'wallet_balance' in st.session_state:
        with open('wallet.csv', 'w') as f:
            writer = csv.DictWriter(f, fieldnames=['balance'])
            writer.writeheader()
            writer.writerow({'balance': st.session_state.wallet_balance})

def save_coupons():
    if 'available_coupons' in st.session_state:
        with open('available_coupons.csv', 'w') as f:
            writer = csv.DictWriter(f, fieldnames=['coupon', 'count'])
            writer.writeheader()
            for coupon, count in st.session_state.available_coupons.items():
                writer.writerow({'coupon': coupon, 'count': count})
    
    if 'redeemed_coupons' in st.session_state:
        with open('redeemed_coupons.csv', 'w') as f:
            writer = csv.DictWriter(f, fieldnames=['coupon', 'count'])
            writer.writeheader()
            for coupon, count in st.session_state.redeemed_coupons.items():
                writer.writerow({'coupon': coupon, 'count': count})

def save_all_data():
    save_reports()
    save_votes()
    save_testimonials()
    save_wallet()
    save_coupons()

# Initialize data files if they don't exist
for file in ['reports.csv', 'votes.csv', 'testimonials.csv', 
            'wallet.csv', 'available_coupons.csv', 'redeemed_coupons.csv']:
    if not os.path.exists(file):
        with open(file, 'w') as f:
            pass  # Create empty file

# Load initial data
load_data()

# Initialize session state
if 'reports' not in st.session_state:
    st.session_state.reports = []
if 'votes' not in st.session_state:
    st.session_state.votes = {}
if 'testimonials' not in st.session_state:
    st.session_state.testimonials = {}
if 'wallet_balance' not in st.session_state:
    st.session_state.wallet_balance = 0
if 'available_coupons' not in st.session_state:
    st.session_state.available_coupons = {}
if 'redeemed_coupons' not in st.session_state:
    st.session_state.redeemed_coupons = {}

COUPONS = {
    "Ration Coupon": {"cost": 50, "validity": 30, "color": "#4682B4", "icon": "🛒"},
    "Water Coupon": {"cost": 30, "validity": 15, "color": "#5F9EA0", "icon": "💧"},
    "Electricity Bill Coupon": {"cost": 70, "validity": 45, "color": "#8B4513", "icon": "💡"},
    "Seed Coupon": {"cost": 40, "validity": 60, "color": "#6B8E23", "icon": "🌱"},
    "Medical Coupon": {"cost": 60, "validity": 30, "color": "#4169E1", "icon": "🏥"},
    "Education Coupon": {"cost": 80, "validity": 90, "color": "#D2691E", "icon": "📚"}
}

CATEGORIES = [
    "Road Damage", "Streetlight Issue", "Garbage", "Water Leakage",
    "Sewage Problem", "Public Safety", "Noise Pollution", "Other"
]

SEVERITY_LEVELS = {
    "Mild": "🟢 Low impact",
    "Moderate": "🟡 Needs attention",
    "Severe": "🔴 Critical issue"
}

# Set page config
st.set_page_config(page_title="CivicSense", page_icon="🏛", layout="wide")

def set_custom_style():
    st.markdown("""
    <style>
    .stApp {
        background-color: #f0f2f6;
        color: #000000;
    }
    .stMarkdown, .stMarkdown p, .stMarkdown strong, .stMarkdown em, 
    .stTextInput label, .stSelectbox label, .stTextArea label,
    .stButton>button, .stExpander label, .stMetric {
        color: #000000 !important;
    }
    .feature-card {
        background-color: white;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        margin-bottom: 20px;
        border: 1px solid #e0e0e0;
        height: 300px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .stButton>button {
        border-radius: 8px;
        border: none;
        padding: 10px 20px;
        font-weight: 500;
        transition: all 0.3s;
        background-color: #4a6fa5;
        color: white !important;
    }
    .coupon-card {
        background: linear-gradient(135deg, {color} 0%, #f8f8f8 100%);
        border-radius: 12px;
        padding: 15px;
        margin: 10px 0;
        border: 1px dashed #666;
        position: relative;
        overflow: hidden;
        color: #000000 !important;
    }
    .header-box {
        background-color: #4a6fa5;
        color: white !important;
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

set_custom_style()

with st.container():
    st.markdown("""
    <div class="header-box">
        <h1 style="color:white !important; margin:0;">🏛 CivicSense</h1>
        <p style="color:white !important; margin:0;">Community Issue Reporting System</p>
    </div>
    """, unsafe_allow_html=True)

def show_wallet():
    cols = st.columns([4, 1])
    with cols[1]:
        if st.button(f"💰 Wallet: {st.session_state.wallet_balance} Points", use_container_width=True):
            st.session_state.current_page = "wallet"
            st.rerun()

if 'current_page' not in st.session_state:
    st.session_state.current_page = "home"

def generate_problem_name(description):
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(
            f"Generate a concise 3-5 word problem name from this description: {description}"
        )
        return response.text.strip('"')
    except:
        return description[:30] + "..." if len(description) > 30 else description

genai.configure(api_key = "YOUR_API_KEY")
video_model = genai.GenerativeModel('gemini-2.0-flash')

if st.session_state.current_page == "home":
    show_wallet()
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <h2>Make Your Community Better</h2>
        <p>Report issues, vote on priorities, and earn rewards for your civic engagement</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        if st.button("📝 Report an Issue", key="report_btn", use_container_width=True):
            st.session_state.current_page = "report"
            st.rerun()
        st.markdown("""
        <div style="text-align: center;">
            <p>Report problems in your community with text, images, or videos</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        if st.button("🗳 Vote on Issues", key="vote_btn", use_container_width=True):
            st.session_state.current_page = "vote"
            st.rerun()
        st.markdown("""
        <div style="text-align: center;">
            <p>Help prioritize community issues by voting on existing reports</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        if st.button("💰 View Wallet", key="wallet_btn", use_container_width=True):
            st.session_state.current_page = "wallet"
            st.rerun()
        st.markdown("""
        <div style="text-align: center;">
            <p>Earn points and redeem coupons for your civic participation</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.current_page == "report":
    show_wallet()
    with st.container():
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.header("Report a Community Issue")

        if st.button("← Back to Home"):
            st.session_state.current_page = "home"
            st.rerun()

        input_type = st.selectbox(
            "How would you like to report the issue?",
            ["Upload Image", "Upload Video", "Upload Audio", "Text Description"],
            index=0
        )

        user_input = None
        if input_type == "Upload Image":
            uploaded_file = st.file_uploader("Upload an image of the issue", type=["jpg", "jpeg", "png"])
            if uploaded_file:
                image = Image.open(uploaded_file)
                st.image(image, caption="Uploaded Image", use_column_width=True)
                user_input = image

        elif input_type == "Upload Video":
            uploaded_file = st.file_uploader("Upload a video (max 20MB)", type=["mp4", "mov"])
            if uploaded_file:
                if uploaded_file.size > 20*1024*1024:
                    st.error("File size too large! Maximum 20MB allowed")
                else:
                    st.video(uploaded_file)
                    video_bytes = uploaded_file.read()
                    user_input = video_bytes

        elif input_type == "Upload Audio":
            uploaded_file = st.file_uploader("Upload an audio description", type=["mp3", "wav"])
            if uploaded_file:
                st.audio(uploaded_file)
                user_input = f"Audio file: {uploaded_file.name}"

        elif input_type == "Text Description":
            user_input = st.text_area("Describe the issue in detail", height=150)

        location = st.text_input("Location (Address or Landmark)")
        reporter_name = st.text_input("Your Name (Optional)")

        if st.button("Generate Report") and (user_input or location):
            with st.spinner("Analyzing your report..."):
                try:
                    analysis = {}
                    if input_type == "Upload Video":
                        response = video_model.generate_content(
                            contents=[
                                {"mime_type": "video/mp4", "data": user_input},
                                f["""You are an expert civic issue analyst. Analyze the uploaded video and generate a short, clear, and informative description of the visible issue. Identify what exactly is happening in the video - whether it's related to rural infrastructure, urban sanitation, waterlogging, garbage accumulation, potholes, damaged public property, blocked drains, or any other public concern.  

Your response should include:  
1. A simple explanation of the problem visible in the video.  
2. The likely type of issue (e.g., overflowing garbage bin, stagnant water, broken road, damaged electric pole).  
3. The severity level (mild, moderate, or severe).  
4. The appropriate department or authority responsible for handling the issue (e.g., municipal sanitation, public works, electricity board).  

Use language that is easy to understand by local authorities or civic bodies for quick action.

Also mention any visible hazards or risks to health and safety. If possible, suggest an immediate action step and how it could benefit the community. This information will help authorities prioritize and respond faster.
"""]
                            ]
                        )
                    elif isinstance(user_input, Image.Image):
                        model = genai.GenerativeModel('gemini-2.0-flash')
                        response = model.generate_content(
                            ["""You are an expert civic issue analyst. Analyze the uploaded image and generate a short, clear, and informative description of the visible issue. Identify what exactly is happening in the image - whether it's related to rural infrastructure, urban sanitation, waterlogging, garbage accumulation, potholes, damaged public property, blocked drains, or any other public concern.  

Your response should include:  
1. A simple explanation of the problem visible in the image.  
2. The likely type of issue (e.g., overflowing garbage bin, stagnant water, broken road, damaged electric pole).  
3. The severity level (mild, moderate, or severe).  
4. The appropriate department or authority responsible for handling the issue (e.g., municipal sanitation, public works, electricity board).  

Use language that is easy to understand by local authorities or civic bodies for quick action.

Also mention any visible hazards or risks to health and safety. If possible, suggest an immediate action step and how it could benefit the community. This information will help authorities prioritize and respond faster."""]
                        )
                    else:
                        model = genai.GenerativeModel('gemini-2.0-flash')
                        prompt = f["""You are an expert civic issue analyst. Analyze the uploaded audio and generate a short, clear, and informative description of the visible issue. Identify what exactly is happening in the audio - whether it's related to rural infrastructure, urban sanitation, waterlogging, garbage accumulation, potholes, damaged public property, blocked drains, or any other public concern.  

Your response should include:  
1. A simple explanation of the problem visible in the audio.  
2. The likely type of issue (e.g., overflowing garbage bin, stagnant water, broken road, damaged electric pole).  
3. The severity level (mild, moderate, or severe).  
4. The appropriate department or authority responsible for handling the issue (e.g., municipal sanitation, public works, electricity board).  

Use language that is easy to understand by local authorities or civic bodies for quick action.

Also mention any visible hazards or risks to health and safety. If possible, suggest an immediate action step and how it could benefit the community. This information will help authorities prioritize and respond faster."""]
                        response = model.generate_content(prompt)

                    try:
                        analysis = json.loads(response.text)
                    except:
                        analysis = {"description": response.text, "category": "Other", "severity": "Moderate"}

                    report_id = str(uuid.uuid4())
                    problem_name = generate_problem_name(analysis['description'])

                    report = {
                        "id": report_id,
                        "problem_name": problem_name,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "description": analysis.get("description", "No description"),
                        "category": analysis.get("category", "Other"),
                        "severity": analysis.get("severity", "Moderate"),
                        "location": location,
                        "reporter": reporter_name or "Anonymous",
                        "status": "Pending",
                        "votes": 0,
                        "input_type": input_type
                    }

                    st.session_state.reports.append(report)
                    st.session_state.wallet_balance += 10
                    save_all_data()
                    st.success("Report generated successfully! +10 points added to your wallet!")

                    st.subheader("Generated Report")
                    cols = st.columns([1, 3])
                    with cols[0]:
                        st.metric("Problem Name", problem_name)
                        st.metric("Severity", SEVERITY_LEVELS[report['severity']])
                    with cols[1]:
                        st.write(f"Category: {report['category']}")
                        st.write(f"Location: {report['location']}")
                        st.write(f"Description: {report['description']}")
                    if st.button("Submit Report"):
                        st.success("Report submitted successfully!")
                        time.sleep(1)
                        st.session_state.current_page = "home"
                        st.rerun()

                except Exception as e:
                    st.error(f"Error: {str(e)}")
        st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.current_page == "vote":
    show_wallet()
    with st.container():
        st.markdown('', unsafe_allow_html=True)
        st.header("Vote on Community Issues")
        if st.button("← Back to Home"):
            st.session_state.current_page = "home"
            st.rerun()

        if not st.session_state.reports:
            st.info("No reports available yet.")
        else:
            st.markdown("## 🏆 Top Priority Issues - Community Leaderboard")
            sorted_reports = sorted(st.session_state.reports, key=lambda x: x['votes'], reverse=True)
            leaderboard_data = []

            for idx, report in enumerate(sorted_reports[:5]):
                leaderboard_data.append({
                    "Rank": idx+1,
                    "Problem": report['problem_name'],
                    "Location": report['location'],
                    "Category": report['category'],
                    "Severity": report['severity'],
                    "Votes": report['votes'],
                    "Status": report['status']
                })

            if leaderboard_data:
                with st.container():
                    for idx, item in enumerate(leaderboard_data):
                        st.markdown('<div class="leaderboard-item">', unsafe_allow_html=True)
                        cols = st.columns([0.5, 2, 2, 1.5, 1.5, 2])
                        with cols[0]:
                            if idx == 0:
                                st.markdown(f"<p style='color:#ffd700; font-weight:bold;'>🥇 {item['Rank']}</p>", unsafe_allow_html=True)
                            elif idx == 1:
                                st.markdown(f"<p style='color:#c0c0c0; font-weight:bold;'>🥈 {item['Rank']}</p>", unsafe_allow_html=True)
                            elif idx == 2:
                                st.markdown(f"<p style='color:#cd7f32; font-weight:bold;'>🥉 {item['Rank']}</p>", unsafe_allow_html=True)
                            else:
                                st.write(f"#{item['Rank']}")

                        with cols[1]:
                            st.write(f"{item['Problem']}")
                            st.caption(item['Category'])

                        with cols[2]:
                            st.write(f"📍 {item['Location']}")

                        with cols[3]:
                            st.write(SEVERITY_LEVELS[item['Severity']])

                        with cols[4]:
                            st.metric("Votes", item['Votes'])

                        with cols[5]:
                            status_color = {
                                "Pending": "gray",
                                "In Progress": "orange",
                                "Resolved": "green"
                            }
                            st.markdown(f"<span style='color:{status_color[item['Status']]};'>{item['Status']}</span>",
                                      unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)

            st.subheader("All Community Issues")
            for report in sorted_reports:
                with st.expander(f"{report['problem_name']} - {report['severity'].capitalize()} Issue", expanded=False):
                    cols = st.columns([3, 1])
                    with cols[0]:
                        st.write(f"Category: {report['category']}")
                        st.write(f"Description: {report['description']}")
                        st.write(f"Location: 📍 {report['location']}")

                    with cols[1]:
                        user_voted = st.session_state.votes.get(report['id'], False)
                        votes = report['votes']

                        if user_voted:
                            st.success("✓ You've voted")
                            st.write(f"Total votes: {votes}")
                            if st.session_state.testimonials.get(report['id']):
                                st.caption(f"Your note: {st.session_state.testimonials[report['id']]}")
                        else:
                            with st.form(key=f"vote_form_{report['id']}"):
                                testimonial = st.text_input("Add a note (optional)",
                                                           key=f"testimonial_{report['id']}")
                                if st.form_submit_button(f"👍 Upvote ({votes})"):
                                    report['votes'] += 1
                                    st.session_state.votes[report['id']] = True
                                    if testimonial:
                                        st.session_state.testimonials[report['id']] = testimonial
                                    if st.session_state.get('last_voted_id') != report['id']:
                                        st.session_state.wallet_balance += 5
                                        st.success("+5 points added to your wallet!")
                                        st.session_state.last_voted_id = report['id']
                                    save_all_data()
                                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
elif st.session_state.current_page == "wallet":
    show_wallet()
    with st.container():
        st.markdown('', unsafe_allow_html=True)
        st.header("Digital Wallet")
        if st.button("← Back to Home"):
            st.session_state.current_page = "home"
            st.rerun()

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("🛒 Buy Coupons")
            for coupon, details in COUPONS.items():
                st.markdown(
                    f"""
                    <div class="coupon-card" style="--color: {details['color']}">
                        <div class="coupon-title">
                            <span class="coupon-icon">{details['icon']}</span>
                            {coupon}
                        </div>
                        <div>Valid for {details['validity']} days</div>
                        <div class="coupon-points">{details['cost']} points</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                if st.button(f"Buy {coupon}", key=f"buy_{coupon}"):
                    if st.session_state.wallet_balance >= details['cost']:
                        st.session_state.wallet_balance -= details['cost']
                        st.session_state.available_coupons[coupon] = st.session_state.available_coupons.get(coupon, 0) + 1
                        save_all_data()
                        st.success(f"Purchased {coupon}!")
                        st.rerun()
                    else:
                        st.error("Insufficient balance!")

        with col2:
            st.subheader("✅ Redeemed Coupons")
            if not st.session_state.redeemed_coupons:
                st.info("No coupons redeemed yet")
            else:
                for coupon, count in st.session_state.redeemed_coupons.items():
                    details = COUPONS.get(coupon, {"color": "#CCCCCC", "icon": "🎫"})
                    st.markdown(
                        f"""
                        <div class="coupon-card" style="background: #f0f0f0; color: #000;">
                            <div class="coupon-title">
                                <span class="coupon-icon">{details['icon']}</span>
                                {coupon}
                            </div>
                            <div style="text-decoration: line-through;">Valid for {details.get('validity', 0)} days</div>
                            <div>Redeemed: {count}x</div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

            st.subheader("🎁 Your Available Coupons")
            if not st.session_state.available_coupons:
                st.info("No coupons available yet")
            else:
                for coupon, count in st.session_state.available_coupons.items():
                    details = COUPONS.get(coupon, {"color": "#4a6fa5", "icon": "🎫", "validity": 30})
                    st.markdown(
                        f"""
                        <div class="coupon-card" style="--color: {details['color']}">
                            <div class="coupon-title">
                                <span class="coupon-icon">{details['icon']}</span>
                                {coupon}
                            </div>
                            <div>Valid for {details['validity']} days</div>
                            <div>Quantity: {count}</div>
                            <div class="coupon-points">{details.get('cost', 0)} points</div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    if st.button(f"Redeem {coupon}", key=f"redeem_{coupon}"):
                        if st.session_state.available_coupons[coupon] > 0:
                            st.session_state.available_coupons[coupon] -= 1
                            if st.session_state.available_coupons[coupon] == 0:
                                del st.session_state.available_coupons[coupon]
                            st.session_state.redeemed_coupons[coupon] = st.session_state.redeemed_coupons.get(coupon, 0) + 1
                            save_all_data()
                            st.success(f"Redeemed {coupon}!")
                            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

if name == "main":
    pass
