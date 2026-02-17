import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import ta

st.set_page_config(layout="wide")
st.title("🔥 AI XAUUSD PRO Smart Money System")

# Timeframe selector
timeframe = st.selectbox("Select Timeframe", ["1h", "4h", "1d"])

# Download Data
data = yf.download("GC=F", period="3mo", interval=timeframe)

# Check if data loaded
if data.empty:
    st.error("❌ No data loaded. Try different timeframe.")
    st.stop()

data.dropna(inplace=True)

# ATR Calculation (Safe)
try:
    atr_indicator = ta.volatility.AverageTrueRange(
        high=data['High'],
        low=data['Low'],
        close=data['Close']
    )
    data['ATR'] = atr_indicator.average_true_range()
except:
    data['ATR'] = np.nan

# Swing Detection
data['Swing_High'] = data['High'][
    (data['High'] > data['High'].shift(1)) &
    (data['High'] > data['High'].shift(-1))
]

data['Swing_Low'] = data['Low'][
    (data['Low'] < data['Low'].shift(1)) &
    (data['Low'] < data['Low'].shift(-1))
]

# ==============================
# Break of Structure (SAFE)
# ==============================

bos_signal = "Neutral"

if len(data) > 25:

    latest_close = data['Close'].iloc[-1]

    prev_high_series = data['High'].rolling(20).max()
    prev_low_series = data['Low'].rolling(20).min()

    prev_high = prev_high_series.iloc[-2]
    prev_low = prev_low_series.iloc[-2]

    if pd.notna(prev_high) and pd.notna(prev_low):

        if latest_close > prev_high:
            bos_signal = "Bullish BOS 🚀"

        elif latest_close < prev_low:
            bos_signal = "Bearish BOS 🔻"

# ==============================
# Liquidity Sweep (SAFE)
# ==============================

liquidity = "No Sweep"

if len(data) > 25:

    if pd.notna(prev_high) and pd.notna(prev_low):

        if data['High'].iloc[-2] > prev_high and latest_close < prev_high:
            liquidity = "Buy Side Liquidity Sweep 🔥"

        elif data['Low'].iloc[-2] < prev_low and latest_close > prev_low:
            liquidity = "Sell Side Liquidity Sweep 🔥"

# ==============================
# Stop Loss Suggestion (ATR Based)
# ==============================

stop_loss = "N/A"

if pd.notna(data['ATR'].iloc[-1]):

    atr_value = data['ATR'].iloc[-1]

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
col3.metric("Suggested SL (ATR)", stop_loss)

# ==============================
# Candlestick Chart
# ==============================

fig = go.Figure(data=[go.Candlestick(
    x=data.index,
    open=data['Open'],
    high=data['High'],
    low=data['Low'],
    close=data['Close']
)])

fig.update_layout(
    title="XAUUSD Chart",
    xaxis_rangeslider_visible=False,
    template="plotly_dark"
)

st.plotly_chart(fig, use_container_width=True)
