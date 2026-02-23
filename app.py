import streamlit as st
import requests

# ==============================
# Session State Init
# ==============================

if "token" not in st.session_state:
    st.session_state.token = None

if "username" not in st.session_state:
    st.session_state.username = None

API_BASE_URL = "https://your-backend-url.onrender.com"

# ==============================
# FUNCTIONS
# ==============================

def register(username, password):
    response = requests.post(
        f"{API_BASE_URL}/register",
        json={"username": username, "password": password}
    )

    if response.status_code == 200:
        st.success("Registration successful ✅ Please login.")
    else:
        st.error("Registration failed ❌")

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

def logout():
    st.session_state.token = None
    st.session_state.username = None

# ==============================
# UI
# ==============================

st.title("🏏 IPL Win Predictor")

if st.session_state.token is None:

    choice = st.radio("Choose Option", ["Login", "Register"])

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if choice == "Login":
        if st.button("Login"):
            login(username, password)

    if choice == "Register":
        if st.button("Register"):
            register(username, password)

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
            st.success(response.json())
        else:
            st.error("Prediction failed ❌")
