import streamlit as st
import requests
import os

# =====================================
# CONFIG
# =====================================

BACKEND_URL = os.getenv("BACKEND_URL")

if not BACKEND_URL:
    st.error("❌ BACKEND_URL not set in Render environment variables")
    st.stop()

# =====================================
# BACKGROUND IMAGE (GitHub RAW LINK)
# =====================================

def set_bg():
    st.markdown(
        """
        <style>
        .stApp {
            background-image: url("https://github.com/ruchika250/ipl-win-predictor/blob/main/background.jpg");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }
        .block-container {
            background: rgba(0,0,0,0.7);
            padding: 2rem;
            border-radius: 15px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

set_bg()

# =====================================
# SESSION INIT
# =====================================

if "token" not in st.session_state:
    st.session_state.token = None

# =====================================
# TITLE
# =====================================

st.title("🏏 IPL Win Probability Predictor")

# =====================================
# AUTH SECTION
# =====================================

if not st.session_state.token:

    st.sidebar.title("🔐 Authentication")
    option = st.sidebar.radio("Select Option", ["Login", "Register"])

    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")

    # -------- REGISTER --------
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
                st.sidebar.error(f"Error {res.status_code}")
                st.sidebar.error(res.text)

    # -------- LOGIN --------
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
                st.sidebar.error("Invalid username or password ❌")

# =====================================
# MAIN APP AFTER LOGIN
# =====================================

else:

    st.sidebar.success("🟢 Logged In")

    if st.sidebar.button("Logout"):
        st.session_state.token = None
        st.rerun()

    # -------- TEAMS & CITY --------

    teams = [
        "Chennai Super Kings",
        "Mumbai Indians",
        "Royal Challengers Bangalore",
        "Kolkata Knight Riders",
        "Delhi Capitals",
        "Rajasthan Royals",
        "Sunrisers Hyderabad",
        "Punjab Kings",
        "Lucknow Super Giants",
        "Gujarat Titans"
    ]

    cities = [
        "Mumbai",
        "Chennai",
        "Kolkata",
        "Delhi",
        "Bangalore",
        "Hyderabad",
        "Jaipur",
        "Ahmedabad",
        "Lucknow",
        "Mohali"
    ]

    st.subheader("📊 Enter Match Details")

    batting_team = st.selectbox("Batting Team", teams)
    bowling_team = st.selectbox("Bowling Team", teams)
    city = st.selectbox("Match City", cities)

    if batting_team == bowling_team:
        st.warning("⚠️ Batting and Bowling team cannot be same")
        st.stop()

    total_runs = st.number_input("Total Runs", min_value=0)

    wickets = st.slider("Wickets Fallen", 0, 10, 0)  # line wala option ✅

    overs = st.number_input("Overs Completed", min_value=0.0)

    runs_left = st.number_input("Runs Left", min_value=0)
    balls_left = st.number_input("Balls Left", min_value=0)

    wickets_left = st.slider("Wickets Left", 0, 10, 10)  # slider line ✅

    target = st.number_input("Target", min_value=0)

    # -------- PREDICTION --------

    if st.button("Predict Win Probability"):

        headers = {
            "Authorization": f"Bearer {st.session_state.token}"
        }

        payload = {
            "customer": {
                "batting_team": batting_team,
                "bowling_team": bowling_team,
                "city": city,
                "total_runs": total_runs,
                "wickets": wickets,
                "overs": overs,
                "runs_left": runs_left,
                "balls_left": balls_left,
                "wickets_left": wickets_left,
                "target": target
            }
        }

        res = requests.post(
            f"{BACKEND_URL}/predict/auth",
            json=payload,
            headers=headers
        )

        if res.status_code == 200:
            data = res.json()
            st.success(f"🏆 Win Probability: {round(data['win_probability']*100,2)}%")
            st.info(f"❌ Loss Probability: {round(data['loss_probability']*100,2)}%")
        else:
            st.error(f"Prediction failed ({res.status_code})")
            st.error(res.text)
