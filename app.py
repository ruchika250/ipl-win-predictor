import streamlit as st
import requests
import os

# ==============================
# CONFIG
# ==============================

BACKEND_URL = os.getenv("BACKEND_URL")

if not BACKEND_URL:
    st.error("❌ BACKEND_URL not set in environment variables")
    st.stop()

# ==============================
# SESSION INIT
# ==============================

if "token" not in st.session_state:
    st.session_state.token = None

# ==============================
# PAGE TITLE
# ==============================

st.set_page_config(page_title="IPL Win Predictor", layout="centered")
st.title("🏏 IPL Win Probability Predictor")

# ==============================
# AUTH SECTION
# ==============================

if not st.session_state.token:

    st.sidebar.title("🔐 Authentication")
    auth_option = st.sidebar.radio("Choose option", ["Login", "Register"])

    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")

    # REGISTER
    if auth_option == "Register":
        if st.sidebar.button("Register"):
            res = requests.post(
                f"{BACKEND_URL}/register",
                json={"username": username, "password": password}
            )

            if res.status_code == 200:
                data = res.json()
                st.session_state.token = data.get("access_token")
                st.sidebar.success("🎉 Registered & Logged in Successfully")
                st.rerun()
            else:
                st.sidebar.error(res.json().get("detail", "Registration failed ❌"))

    # LOGIN
    if auth_option == "Login":
        if st.sidebar.button("Login"):
            res = requests.post(
                f"{BACKEND_URL}/login",
                json={"username": username, "password": password}
            )

            if res.status_code == 200:
                data = res.json()
                st.session_state.token = data.get("access_token")
                st.sidebar.success("✅ Logged in Successfully")
                st.rerun()
            else:
                st.sidebar.error("Invalid username or password ❌")

# ==============================
# MAIN APP (AFTER LOGIN)
# ==============================

else:

    st.sidebar.success("🟢 Logged In")
    if st.sidebar.button("Logout"):
        st.session_state.token = None
        st.rerun()

    st.subheader("Match Details")

    batting_team = st.selectbox("Batting Team", [
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
    ])

    bowling_team = st.selectbox("Bowling Team", [
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
    ])

    total_runs = st.number_input("Total Runs", min_value=0)
    wickets = st.number_input("Wickets Fallen", min_value=0, max_value=10)
    overs = st.number_input("Overs Completed", min_value=0.0)
    runs_left = st.number_input("Runs Left", min_value=0)
    balls_left = st.number_input("Balls Left", min_value=0)
    wickets_left = st.number_input("Wickets Left", min_value=0, max_value=10)
    target = st.number_input("Target", min_value=0)

    if st.button("Predict Win Probability"):

        headers = {
            "Authorization": f"Bearer {st.session_state.token}"
        }

        payload = {
            "customer": {
                "batting_team": batting_team,
                "bowling_team": bowling_team,
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
            st.error("Prediction failed ❌")
