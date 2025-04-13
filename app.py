import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import time

# Page config
st.set_page_config(page_title="Contacts Generator", layout="wide")

st.title("Contacts Generator")
st.markdown("Simulates 15-minute interval contact data across multiple channels. Auto-refreshes every 15 seconds.")

# Sidebar Inputs
st.sidebar.header("Simulation Settings")

total_contacts_per_hour = st.sidebar.slider("Total Contacts per Hour", 100, 2000, 500, step=50)

# Channel Mix Sliders (ensure they sum to 100%)
st.sidebar.subheader("Channel Mix (%)")

default_mix = {"Voice": 40, "Chat": 30, "Email": 20, "SMS": 10}

voice_percent = st.sidebar.slider("Voice", 0, 100, default_mix["Voice"])
chat_percent = st.sidebar.slider("Chat", 0, 100, default_mix["Chat"])
email_percent = st.sidebar.slider("Email", 0, 100, default_mix["Email"])
sms_percent = st.sidebar.slider("SMS", 0, 100, default_mix["SMS"])

# Normalize if total != 100%
total_percent = voice_percent + chat_percent + email_percent + sms_percent
if total_percent != 100:
    st.sidebar.warning("Percentages don't add up to 100%. Normalizing automatically.")
    total = voice_percent + chat_percent + email_percent + sms_percent
    voice_percent = voice_percent / total * 100
    chat_percent = chat_percent / total * 100
    email_percent = email_percent / total * 100
    sms_percent = sms_percent / total * 100

# --- Generate Data ---
intervals = pd.date_range(start="08:00", end="17:45", freq="15min")
contacts_per_interval = total_contacts_per_hour / 4

# Simulate Poisson-distributed contacts per channel
data = pd.DataFrame({
    "Interval": intervals,
    "Voice": np.random.poisson(contacts_per_interval * (voice_percent / 100), len(intervals)),
    "Chat": np.random.poisson(contacts_per_interval * (chat_percent / 100), len(intervals)),
    "Email": np.random.poisson(contacts_per_interval * (email_percent / 100), len(intervals)),
    "SMS": np.random.poisson(contacts_per_interval * (sms_percent / 100), len(intervals)),
})

data["Total"] = data[["Voice", "Chat", "Email", "SMS"]].sum(axis=1)

# --- Visualization ---
fig = px.bar(
    data,
    x="Interval",
    y=["Voice", "Chat", "Email", "SMS"],
    title="Simulated Contacts by Channel (15-Minute Intervals)",
    labels={"value": "Contacts", "Interval": "Time"},
    barmode="stack"
)

st.plotly_chart(fig, use_container_width=True)

# --- Optional Raw Data ---
if st.checkbox("Show Raw Data"):
    st.dataframe(data)

# --- Auto-refresh every 15 seconds ---
st.markdown("Auto-refreshing every **15 seconds**...")
st_autorefresh = st.experimental_rerun if "streamlit_autorefresh" not in st.session_state else None
time.sleep(15)
st.experimental_rerun()