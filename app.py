import streamlit as st
import requests

# ==============================
# Session State Initialization
# ==============================

if "token" not in st.session_state:
    st.session_state.token = None

if "username" not in st.session_state:
    st.session_state.username = None

# ==============================
# CONFIG
# ==============================

API_BASE_URL = "https://ipl-win-predictor-api.onrender.com"
# 👆 yaha apna FastAPI backend URL daalna

# ==============================
# Login Function
# ==============================

def login(username, password):
    response = requests.post(
        f"{API_BASE_URL}/login",
        json={"username": username, "password": password}
    )

    if response.status_code == 200:
        data = response.json()
        st.session_state.token = data.get("access_token")
        st.session_state.username = username
        st.success("Login successful ✅")
    else:
        st.error("Invalid credentials ❌")

# ==============================
# Logout
# ==============================

def logout():
    st.session_state.token = None
    st.session_state.username = None
    st.success("Logged out successfully")

# ==============================
# UI START
# ==============================

st.title("🏏 IPL Win Predictor")

# ==============================
# If NOT Logged In
# ==============================

if st.session_state.token is None:

    st.subheader("Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        login(username, password)

# ==============================
# If Logged In
# ==============================

else:
    st.success(f"Welcome {st.session_state.username} 🎉")

    if st.button("Logout"):
        logout()

    st.subheader("Match Prediction")

    team1 = st.text_input("Team 1")
    team2 = st.text_input("Team 2")
    target = st.number_input("Target Score", min_value=0)

    if st.button("Predict"):
        headers = {
            "Authorization": f"Bearer {st.session_state.token}"
        }

        response = requests.post(
            f"{API_BASE_URL}/predict",
            json={
                "batting_team": team1,
                "bowling_team": team2,
                "target": target
            },
            headers=headers
        )

        if response.status_code == 200:
            result = response.json()
            st.success(f"Win Probability: {result}")
        else:
            st.error("Prediction failed ❌")
