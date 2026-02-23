import streamlit as st
import pickle
import pandas as pd
import base64
import requests

# -------------------------------
# Page Config
# -------------------------------
st.set_page_config(
    page_title="IPL Win Predictor",
    page_icon="🏏",
    layout="centered"
)

API_URL = "http://127.0.0.1:8000"

# -------------------------------
# Background Image Loader
# -------------------------------
def add_bg(image_file):
    with open(image_file, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()

    st.markdown(
        f"""
        <style>
        .stApp {{
            background: url(data:image/jpg;base64,{encoded});
            background-size: cover;
            background-position: center;
        }}

        .glass {{
            background: rgba(0, 0, 0, 0.7);
            backdrop-filter: blur(10px);
            padding: 30px;
            border-radius: 20px;
            color: white;
        }}

        .title {{
            text-align: center;
            font-size: 45px;
            font-weight: 800;
            color: #FFD700;
            text-shadow: 2px 2px 10px black;
        }}

        .sub {{
            text-align: center;
            color: #eee;
            margin-bottom: 30px;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

add_bg("background.jpg")

# -------------------------------
# Auth State
# -------------------------------
if "token" not in st.session_state:
    st.session_state.token = None

# -------------------------------
# Sidebar Authentication UI
# -------------------------------
st.sidebar.title("🔐 Authentication")
mode = st.sidebar.radio("Select Mode", ["Login", "Register"])

username = st.sidebar.text_input("Username")
password = st.sidebar.text_input("Password", type="password")

def safe_api_call(method, url, **kwargs):
    try:
        res = requests.request(method, url, timeout=5, **kwargs)
        return res
    except requests.exceptions.ConnectionError:
        st.sidebar.error("❌ Backend API is not running on port 8000.")
        st.stop()
    except requests.exceptions.Timeout:
        st.sidebar.error("⏱️ Backend API timed out.")
        st.stop()

if mode == "Login":
    if st.sidebar.button("Login"):
        res = safe_api_call("post", f"{API_URL}/login", json={
            "username": username,
            "password": password
        })

        if res.status_code == 200:
            st.session_state.token = res.json()["access_token"]
            st.sidebar.success("Login successful 🎉")
        else:
            try:
                st.sidebar.error(res.json().get("detail", "Login failed"))
            except Exception:
                st.sidebar.error(f"API Error {res.status_code}: {res.text}")

if mode == "Register":
    if st.sidebar.button("Register"):
        res = safe_api_call("post", f"{API_URL}/register", json={
            "username": username,
            "password": password
        })

        if res.status_code == 200:
            st.sidebar.success("Registered successfully 🎉 Now login.")
        else:
            try:
                st.sidebar.error(res.json().get("detail", "Registration failed"))
            except Exception:
                st.sidebar.error(f"API Error {res.status_code}: {res.text}")

if st.session_state.token:
    if st.sidebar.button("Logout"):
        st.session_state.token = None
        st.sidebar.success("Logged out!")

# -------------------------------
# Load Model
# -------------------------------
pipe = pickle.load(open('pipe.pkl','rb'))

teams = [
    "Chennai Super Kings", "Mumbai Indians", "Kolkata Knight Riders",
    "Royal Challengers Bengaluru", "Delhi Capitals", "Sunrisers Hyderabad",
    "Rajasthan Royals", "Punjab Kings", "Gujarat Titans", "Lucknow Super Giants"
]

cities = [
    'Hyderabad','Bangalore','Mumbai','Indore','Kolkata','Delhi','Chandigarh',
    'Jaipur','Chennai','Cape Town','Port Elizabeth','Durban','Centurion',
    'East London','Johannesburg','Kimberley','Bloemfontein','Ahmedabad',
    'Cuttack','Nagpur','Dharamsala','Visakhapatnam','Pune','Raipur','Ranchi',
    'Abu Dhabi','Sharjah','Mohali','Bengaluru'
]

# -------------------------------
# UI
# -------------------------------
st.markdown("<div class='title'>🏏 IPL Win Predictor</div>", unsafe_allow_html=True)
st.markdown("<div class='sub'>Predict your team’s victory in real-time</div>", unsafe_allow_html=True)

with st.container():
    st.markdown("<div class='glass'>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        batting_team = st.selectbox("Batting Team", teams)
    with col2:
        bowling_team = st.selectbox("Bowling Team", teams)

    city = st.selectbox("Host City", cities)

    col3, col4, col5 = st.columns(3)
    with col3:
        target = st.number_input("Target", min_value=1)
    with col4:
        score = st.number_input("Current Score", min_value=0)
    with col5:
        overs = st.number_input("Overs Completed", min_value=0.1, max_value=20.0)

    wickets = st.slider("Wickets Fallen", 0, 10, 2)

    if st.button("🔥 Predict Match Outcome"):

        if not st.session_state.token:
            st.error("🔐 Please login first to predict!")
            st.stop()

        payload = {
            "customer": {
                "batting_team": batting_team,
                "bowling_team": bowling_team,
                "city": city,
                "target": target,
                "score": score,
                "wickets": wickets,
                "overs": overs
            }
        }

        headers = {
            "Authorization": f"Bearer {st.session_state.token}"
        }

        res = safe_api_call("post", f"{API_URL}/predict/auth", json=payload, headers=headers)

        if res.status_code == 200:
            data = res.json()
            st.success(f"🏆 {data['batting_team']} Win Chance: {data['win_probability']:.2f}%")
            st.error(f"💔 {data['bowling_team']} Win Chance: {data['loss_probability']:.2f}%")
        else:
            try:
                st.error(res.json().get("detail", "Token expired or invalid. Please login again."))
            except Exception:
                st.error(f"API Error {res.status_code}: {res.text}")

    st.markdown("</div>", unsafe_allow_html=True)