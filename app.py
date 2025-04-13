import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, time as dtime

st.set_page_config(page_title="Contact Generator", layout="wide")
st.title("Contact Generator")
st.markdown("Simulate 15-minute interval contact volume by channel, with common or custom arrival patterns.")

# --- Sidebar Controls ---
st.sidebar.header("Simulation Settings")

# Operating hours
start_time = st.sidebar.time_input("Start Time", dtime(8, 0))
end_time = st.sidebar.time_input("End Time", dtime(17, 0))

# Contact volume
total_contacts_per_hour = st.sidebar.slider("Contacts per Hour", 100, 2000, 500, step=50)

# Channel mix
st.sidebar.subheader("Channel Mix (%)")
voice_pct = st.sidebar.slider("Voice", 0, 100, 50)
chat_pct = st.sidebar.slider("Chat", 0, 100, 30)
email_pct = st.sidebar.slider("Email", 0, 100, 20)

# Normalize if needed
total_pct = voice_pct + chat_pct + email_pct
if total_pct != 100:
    st.sidebar.warning("Channel mix doesn't sum to 100%. Normalizing automatically.")
    voice_pct = voice_pct / total_pct * 100
    chat_pct = chat_pct / total_pct * 100
    email_pct = email_pct / total_pct * 100

# --- Time Intervals Setup ---
start_dt = datetime.combine(datetime.today(), start_time)
end_dt = datetime.combine(datetime.today(), end_time)
intervals = pd.date_range(start=start_dt, end=end_dt, freq="15min")[:-1]
num_intervals = len(intervals)

# --- Common Arrival Patterns ---
def generate_pattern(pattern_name):
    x = np.linspace(0, 1, num_intervals)
    if pattern_name == "Flat":
        return np.ones(num_intervals)
    elif pattern_name == "Morning Peak":
        return np.exp(-5 * (x - 0.3)**2)
    elif pattern_name == "Afternoon Peak":
        return np.exp(-5 * (x - 0.7)**2)
    elif pattern_name == "Midday Spike":
        return np.exp(-6 * (x - 0.5)**2)
    elif pattern_name == "U-Shape":
        return 1 - np.abs(0.5 - x)
    elif pattern_name == "Bell Curve":
        return np.exp(-6 * (x - 0.5)**2)
    elif pattern_name == "Front-Loaded":
        return 1 - x
    elif pattern_name == "Back-Loaded":
        return x
    elif pattern_name == "Double Peaks":
        return np.exp(-8 * (x - 0.3)**2) + np.exp(-8 * (x - 0.7)**2)
    elif pattern_name == "Random":
        np.random.seed(42)
        return np.random.rand(num_intervals)
    else:
        return np.ones(num_intervals)

# --- Arrival Curve Selection ---
st.sidebar.subheader("Arrival Curve")
curve_option = st.sidebar.selectbox("Select a pattern", [
    "Flat", "Morning Peak", "Afternoon Peak", "Midday Spike", "U-Shape",
    "Bell Curve", "Front-Loaded", "Back-Loaded", "Double Peaks", "Random", "Custom"
])

if curve_option != "Custom":
    raw_curve = generate_pattern(curve_option)
    arrival_curve = raw_curve / raw_curve.sum()
    show_curve_df = pd.DataFrame({
        "Interval": intervals.strftime("%H:%M"),
        "Weight": np.round(arrival_curve, 4)
    })
else:
    # Editable custom curve
    st.sidebar.info("Edit the weights manually. Values will be normalized.")
    custom_df = pd.DataFrame({
        "Interval": intervals.strftime("%H:%M"),
        "Weight": [1.0] * num_intervals
    })
    edited_df = st.data_editor(custom_df, use_container_width=True, key="arrival_editor")
    raw_curve = edited_df["Weight"].to_numpy()
    arrival_curve = raw_curve / raw_curve.sum()
    show_curve_df = edited_df.copy()
    show_curve_df["Weight"] = np.round(arrival_curve, 4)

# --- Display Arrival Curve Chart ---
st.subheader("Arrival Curve")
curve_fig = px.bar(
    show_curve_df,
    x="Interval",
    y="Weight",
    title=f"Arrival Curve Pattern: {curve_option}",
    labels={"Weight": "Normalized Weight"},
)
st.plotly_chart(curve_fig, use_container_width=True)

# --- Contact Volume Simulation ---
total_contacts = total_contacts_per_hour * (num_intervals / 4)
contacts_by_interval = np.random.poisson(total_contacts * arrival_curve)

# Channel splits
voice = np.random.poisson(contacts_by_interval * (voice_pct / 100))
chat = np.random.poisson(contacts_by_interval * (chat_pct / 100))
email = np.random.poisson(contacts_by_interval * (email_pct / 100))

data = pd.DataFrame({
    "Interval": intervals,
    "Voice": voice,
    "Chat": chat,
    "Email": email
})
data["Total"] = data[["Voice", "Chat", "Email"]].sum(axis=1)

# --- Display Contact Volume Chart ---
st.subheader("Simulated Contact Volume")
volume_fig = px.bar(
    data,
    x="Interval",
    y=["Voice", "Chat", "Email"],
    title="Contact Volume by Channel",
    labels={"value": "Contacts", "Interval": "Time"},
    barmode="stack"
)
st.plotly_chart(volume_fig, use_container_width=True)

# --- Optional Raw Data ---
with st.expander("Show Raw Data"):
    st.dataframe(data)