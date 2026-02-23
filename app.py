import streamlit as st
import pickle
import pandas as pd
import requests
import os

# ===============================
# CONFIG
# ===============================

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# ===============================
# BACKGROUND IMAGE
# ===============================

import base64

def set_bg():
    with open("background.jpg", "rb") as img_file:
        encoded = base64.b64encode(img_file.read()).decode()

    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpg;base64,{encoded}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        .block-container {{
            background: rgba(0,0,0,0.75);
            padding: 2rem;
            border-radius: 15px;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

set_bg()

# ===============================
# SESSION INIT
# ===============================

if "token" not in st.session_state:
    st.session_state.token = None

# ===============================
# LOAD MODEL
# ===============================

pipe = pickle.load(open('pipe.pkl','rb'))

# ===============================
# DATA
# ===============================

teams = [
 'Sunrisers Hyderabad',
 'Mumbai Indians',
 'Royal Challengers Bangalore',
 'Kolkata Knight Riders',
 'Kings XI Punjab',
 'Chennai Super Kings',
 'Rajasthan Royals',
 'Delhi Capitals'
]

cities = [
 'Hyderabad','Bangalore','Mumbai','Indore','Kolkata','Delhi',
 'Chandigarh','Jaipur','Chennai','Cape Town','Port Elizabeth',
 'Durban','Centurion','East London','Johannesburg','Kimberley',
 'Bloemfontein','Ahmedabad','Cuttack','Nagpur','Dharamsala',
 'Visakhapatnam','Pune','Raipur','Ranchi','Abu Dhabi',
 'Sharjah','Mohali','Bengaluru'
]

# ===============================
# TITLE
# ===============================

st.title("🏏 IPL Win Predictor")

# ===============================
# AUTH SECTION
# ===============================

if not st.session_state.token:

    st.sidebar.title("🔐 Authentication")
    option = st.sidebar.radio("Select Option", ["Login", "Register"])

    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")

    if option == "Register":
        if st.sidebar.button("Register"):
            res = requests.post(
                f"{BACKEND_URL}/register",
                json={"username": username, "password": password}
            )
            if res.status_code == 200:
                data = res.json()
                st.session_state.token = data.get("access_token")
                st.sidebar.success("Registered Successfully 🎉")
                st.rerun()
            else:
                st.sidebar.error(res.text)

    if option == "Login":
        if st.sidebar.button("Login"):
            res = requests.post(
                f"{BACKEND_URL}/login",
                json={"username": username, "password": password}
            )
            if res.status_code == 200:
                data = res.json()
                st.session_state.token = data.get("access_token")
                st.sidebar.success("Login Successful ✅")
                st.rerun()
            else:
                st.sidebar.error("Invalid username ❌")

# ===============================
# MAIN APP AFTER LOGIN
# ===============================

else:

    st.sidebar.success("🟢 Logged In")
    if st.sidebar.button("Logout"):
        st.session_state.token = None
        st.rerun()

    # 2 Columns
    col1, col2 = st.columns(2)

    with col1:
        batting_team = st.selectbox('Select the batting team', sorted(teams))
    with col2:
        bowling_team = st.selectbox('Select the bowling team', sorted(teams))

    selected_city = st.selectbox('Select host city', sorted(cities))

    target = st.number_input('Target', min_value=1)

    # 3 Columns
    col3, col4, col5 = st.columns(3)

    with col3:
        score = st.number_input('Score', min_value=0)
    with col4:
        overs = st.number_input('Overs completed', min_value=0.1)
    with col5:
        wickets_out = st.slider('Wickets out', 0, 10, 0)

    if st.button('Predict Probability'):

        if batting_team == bowling_team:
            st.warning("Teams cannot be same ❗")
            st.stop()

        runs_left = target - score
        balls_left = 120 - (overs * 6)
        wickets_left = 10 - wickets_out

        if overs == 0:
            st.error("Overs cannot be 0")
            st.stop()

        crr = score / overs
        rrr = (runs_left * 6) / balls_left if balls_left != 0 else 0

        input_df = pd.DataFrame({
            'batting_team': [batting_team],
            'bowling_team': [bowling_team],
            'city': [selected_city],
            'runs_left': [runs_left],
            'balls_left': [balls_left],
            'wickets': [wickets_left],
            'total_runs_x': [target],
            'crr': [crr],
            'rrr': [rrr]
        })

        result = pipe.predict_proba(input_df)
        loss = result[0][0]
        win = result[0][1]

        st.success(f"🏆 {batting_team} Win Probability: {round(win*100)}%")
        st.error(f"💔 {bowling_team} Win Probability: {round(loss*100)}%")
