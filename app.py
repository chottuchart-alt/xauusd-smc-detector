import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(layout="wide")
st.title("🔥 AI XAUUSD PRO Smart Money System")

# Timeframe selector
timeframe = st.selectbox("Select Timeframe", ["1h", "4h", "1d"])

# Download Data
data = yf.download("GC=F", period="3mo", interval=timeframe)

if data.empty:
    st.error("No data loaded. Try again.")
    st.stop()

data = data.dropna().copy()

# ==============================
# Manual ATR Calculation (SAFE)
# ==============================

data["H-L"] = data["High"] - data["Low"]
data["H-PC"] = abs(data["High"] - data["Close"].shift(1))
data["L-PC"] = abs(data["Low"] - data["Close"].shift(1))

data["TR"] = data[["H-L", "H-PC", "L-PC"]].max(axis=1)
data["ATR"] = data["TR"].rolling(14).mean()

# ==============================
# BOS + Liquidity Logic
# ==============================

bos_signal = "Neutral"
liquidity = "No Sweep"
stop_loss = "N/A"

if len(data) > 30:

    latest_close = float(data["Close"].iloc[-1])

    prev_high = float(data["High"].rolling(20).max().iloc[-2])
    prev_low = float(data["Low"].rolling(20).min().iloc[-2])

    # Break of Structure
    if latest_close > prev_high:
        bos_signal = "Bullish BOS 🚀"
    elif latest_close < prev_low:
        bos_signal = "Bearish BOS 🔻"

    # Liquidity Sweep
    last_high = float(data["High"].iloc[-2])
    last_low = float(data["Low"].iloc[-2])

    if last_high > prev_high and latest_close < prev_high:
        liquidity = "Buy Side Liquidity Sweep 🔥"
    elif last_low < prev_low and latest_close > prev_low:
        liquidity = "Sell Side Liquidity Sweep 🔥"

    # ATR Stop Loss
    atr_value = float(data["ATR"].iloc[-1])

    if bos_signal == "Bullish BOS 🚀":
        stop_loss = round(latest_close - atr_value, 2)
    elif bos_signal == "Bearish BOS 🔻":
        stop_loss = round(latest_close + atr_value, 2)

# ==============================
# Display Metrics
# ==============================

col1, col2, col3 = st.columns(3)

col1.metric("Market Structure", bos_signal)
col2.metric("Liquidity Status", liquidity)
col3.metric("Suggested SL", stop_loss)

# ==============================
# Candlestick Chart
# ==============================

fig = go.Figure(data=[go.Candlestick(
    x=data.index,
    open=data["Open"],
    high=data["High"],
    low=data["Low"],
    close=data["Close"]
)])

fig.update_layout(
    title="XAUUSD Chart",
    xaxis_rangeslider_visible=False,
    template="plotly_dark"
)

st.plotly_chart(fig, use_container_width=True)
