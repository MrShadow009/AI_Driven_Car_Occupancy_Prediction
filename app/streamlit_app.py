
# ================================================================
#  Smart Parking Occupancy Predictor — 3-Page App
#  Pages: Login → Predict → History
#  Run: streamlit run streamlit_app_user.py
# ================================================================

import streamlit as st
import pandas as pd
import numpy as np
import pickle
import os
from datetime import datetime
import warnings
warnings.filterwarnings("ignore")

st.set_page_config(page_title="Smart Parking Predictor", page_icon="🚗", layout="centered")

# ── Load model (silent — no dev messages shown to user) ───────────
BASE_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_DIR = os.path.join(BASE_DIR, "models")

@st.cache_resource
def load_assets():
    model, feature_cols = None, None
    mp = os.path.join(MODEL_DIR, "best_model.pkl")
    fp = os.path.join(MODEL_DIR, "feature_cols.pkl")
    if os.path.exists(mp):
        with open(mp, "rb") as f: model = pickle.load(f)
    if os.path.exists(fp):
        with open(fp, "rb") as f: feature_cols = pickle.load(f)
    return model, feature_cols

model, feature_cols = load_assets()

# ── Session state setup ────────────────────────────────────────────
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_name" not in st.session_state:
    st.session_state.user_name = ""
if "history" not in st.session_state:
    st.session_state.history = []   # list of dicts: {time, label, confidence, zone}


def run_prediction(hour, day_of_week, month, vehicle_type, user_type, zone, spot_size):
    """Build the feature row, run the model, return (label, confidence)."""
    is_weekend      = int(day_of_week >= 5)
    is_morning_peak = int(7  <= hour <= 9)
    is_lunch_hour   = int(12 <= hour <= 14)
    is_evening_peak = int(17 <= hour <= 19)
    is_night        = int(22 <= hour <= 23)
    hour_sin  = np.sin(2 * np.pi * hour        / 24)
    hour_cos  = np.cos(2 * np.pi * hour        / 24)
    day_sin   = np.sin(2 * np.pi * day_of_week / 7)
    day_cos   = np.cos(2 * np.pi * day_of_week / 7)
    month_sin = np.sin(2 * np.pi * month       / 12)
    month_cos = np.cos(2 * np.pi * month       / 12)
    sensor_mean    = 145.0
    sensor_product = 120.0 * 3200.0
    weather_stress = 5.0
    peak_weekday   = is_morning_peak * (1 - is_weekend)
    traffic_level  = "Medium"
    payment_status = "Paid"
    prev_occupancy = 0

    row = {
        "Sensor_Reading_Proximity": 120.0, "Sensor_Reading_Pressure": 3200.0,
        "Sensor_Reading_Ultrasonic": 115.0, "Weather_Temperature": 22.0,
        "Weather_Precipitation": 10.0, "Dynamic_Pricing_Factor": 1.0,
        "Environmental_Noise_Level": 60.0, "Proximity_To_Exit": 50.0,
        "User_Parking_History": 10.0, "Vehicle_Type_Weight": 1200.0,
        "Vehicle_Type_Height": 1.5,
        "Electric_Vehicle": int(vehicle_type == "Electric Vehicle"),
        "Reserved_Status": 0, "Parking_Violation": 0,
        "hour": hour, "day_of_week": day_of_week, "month": month, "day_of_month": 15,
        "is_weekend": is_weekend, "is_morning_peak": is_morning_peak,
        "is_lunch_hour": is_lunch_hour, "is_evening_peak": is_evening_peak,
        "is_night": is_night, "hour_sin": hour_sin, "hour_cos": hour_cos,
        "day_sin": day_sin, "day_cos": day_cos, "month_sin": month_sin, "month_cos": month_cos,
        "prev_occupancy": prev_occupancy, "prev_occupancy_2": prev_occupancy,
        "rolling_mean_3": float(prev_occupancy), "rolling_mean_6": float(prev_occupancy),
        "spot_hour_avg": 0.55, "sensor_product": sensor_product,
        "sensor_mean": sensor_mean, "weather_stress": weather_stress, "peak_weekday": peak_weekday,
        "Vehicle_Type_Motorcycle":       int(vehicle_type == "Motorcycle"),
        "Vehicle_Type_Electric Vehicle": int(vehicle_type == "Electric Vehicle"),
        "Vehicle_Type_Truck":            int(vehicle_type == "Truck"),
        "User_Type_Staff":               int(user_type == "Staff"),
        "User_Type_Visitor":             int(user_type == "Visitor"),
        "Nearby_Traffic_Level_Low":      int(traffic_level == "Low"),
        "Nearby_Traffic_Level_Medium":   int(traffic_level == "Medium"),
        "Parking_Lot_Section_Zone B":    int(zone == "Zone B"),
        "Parking_Lot_Section_Zone C":    int(zone == "Zone C"),
        "Parking_Lot_Section_Zone D":    int(zone == "Zone D"),
        "Spot_Size_Oversized":           int(spot_size == "Oversized"),
        "Spot_Size_Standard":            int(spot_size == "Standard"),
        "Payment_Status_Paid":           int(payment_status == "Paid"),
        "Payment_Status_Unpaid":         int(payment_status == "Unpaid"),
    }

    input_df = pd.DataFrame([row])
    if feature_cols:
        for col in feature_cols:
            if col not in input_df.columns: input_df[col] = 0
        input_df = input_df[feature_cols]

    prob  = model.predict_proba(input_df)[0][1]
    label = "Occupied" if prob >= 0.5 else "Vacant"
    conf  = prob * 100 if label == "Occupied" else (1 - prob) * 100
    return label, conf


# ================================================================
#  PAGE 0 — LOGIN
# ================================================================
if not st.session_state.logged_in:
    st.title("🚗 Smart Parking")
    st.caption("Sign in to check spot availability.")
    st.markdown("---")

    with st.form("login_form"):
        name = st.text_input("Your Name")
        email = st.text_input("Email")
        submitted = st.form_submit_button("Sign In", type="primary", use_container_width=True)

        if submitted:
            if name.strip() == "":
                st.warning("Please enter your name to continue.")
            else:
                st.session_state.logged_in = True
                st.session_state.user_name = name.strip()
                st.rerun()

    st.stop()


# ================================================================
#  Logged in — sidebar navigation
# ================================================================
st.sidebar.title("🚗 Smart Parking")
st.sidebar.caption(f"Signed in as **{st.session_state.user_name}**")
st.sidebar.markdown("---")
page = st.sidebar.radio("Navigate", ["🔮 Predict Occupancy", "🕓 History"])
st.sidebar.markdown("---")
if st.sidebar.button("Log Out", use_container_width=True):
    st.session_state.logged_in = False
    st.session_state.user_name = ""
    st.rerun()

if not model:
    st.error("This service is temporarily unavailable. Please try again shortly.")
    st.stop()


# ================================================================
#  PAGE 1 — PREDICT OCCUPANCY
# ================================================================
if page == "🔮 Predict Occupancy":
    st.title("🅿️ Find a Parking Spot")
    st.caption(f"Hi {st.session_state.user_name} — tell us a few details and we'll check availability.")
    st.markdown("---")

    st.markdown("#### 🕐 When")
    c1, c2, c3 = st.columns(3)
    hour        = c1.selectbox("Time of Day", list(range(24)), index=9,
                                format_func=lambda x: f"{x:02d}:00")
    day_of_week = c2.selectbox("Day", list(range(7)),
                                format_func=lambda x:
                                ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"][x])
    month       = c3.selectbox("Month", list(range(1,13)),
                                format_func=lambda x:
                                ["Jan","Feb","Mar","Apr","May","Jun",
                                 "Jul","Aug","Sep","Oct","Nov","Dec"][x-1])

    st.markdown("#### 🚙 Your Vehicle")
    c1, c2 = st.columns(2)
    vehicle_type   = c1.selectbox("Vehicle Type", ["Car","Motorcycle","Electric Vehicle","Truck"])
    user_type      = c2.selectbox("You are a", ["Visitor","Registered User","Staff"])

    st.markdown("#### 🏙️ Where")
    c1, c2 = st.columns(2)
    zone           = c1.selectbox("Parking Zone",  ["Zone A","Zone B","Zone C","Zone D"])
    spot_size      = c2.selectbox("Spot Size",     ["Standard","Compact","Oversized"])

    st.markdown("---")

    if st.button("🔮 Check Availability", type="primary", use_container_width=True):
        label, conf = run_prediction(hour, day_of_week, month, vehicle_type,
                                      user_type, zone, spot_size)

        # Save to session history
        st.session_state.history.insert(0, {
            "Time": datetime.now().strftime("%I:%M %p"),
            "Zone": zone,
            "Checked For": f"{hour:02d}:00, {['Mon','Tue','Wed','Thu','Fri','Sat','Sun'][day_of_week]}",
            "Result": label,
            "Confidence": f"{conf:.0f}%"
        })

        st.markdown("---")
        if label == "Occupied":
            st.error(f"🔴 **Likely Occupied** — {conf:.0f}% confident")
            st.caption("You may want to check a nearby zone instead.")
        else:
            st.success(f"🟢 **Likely Vacant** — {conf:.0f}% confident")
            st.caption("Good chance this spot is free right now.")


# ================================================================
#  PAGE 2 — HISTORY
# ================================================================
elif page == "🕓 History":
    st.title("🕓 Your Recent Checks")
    st.caption("A log of the spots you've checked this session.")
    st.markdown("---")

    if not st.session_state.history:
        st.info("No checks yet — head to **Predict Occupancy** to look up a spot.")
    else:
        st.dataframe(pd.DataFrame(st.session_state.history),
                     hide_index=True, use_container_width=True)
        if st.button("Clear History"):
            st.session_state.history = []
            st.rerun()


