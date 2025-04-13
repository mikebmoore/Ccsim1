 import streamlit as st
import plotly.express as px
import pandas as pd

st.title("WFM Forecast Example")

# Example data
data = pd.DataFrame({
    "time": ["10:00", "10:15", "10:30", "10:45"],
    "forecast": [22, 24, 23, 26]
})

fig = px.line(data, x="time", y="forecast", title="Forecast Over Time")

st.plotly_chart(fig)