import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

st.title("AI XAUUSD Smart Money Detector")

# Download Gold Data (Futures symbol)
data = yf.download("GC=F", period="1mo", interval="1h")

# Detect Swing High & Low
data['Swing_High'] = data['High'][(data['High'] > data['High'].shift(1)) & 
                                  (data['High'] > data['High'].shift(-1))]

data['Swing_Low'] = data['Low'][(data['Low'] < data['Low'].shift(1)) & 
                                (data['Low'] < data['Low'].shift(-1))]

# Detect Break of Structure (Simple Logic)
latest_close = data['Close'].iloc[-1]
previous_high = data['High'].rolling(20).max().iloc[-2]
previous_low = data['Low'].rolling(20).min().iloc[-2]

signal = "Neutral"

if latest_close > previous_high:
    signal = "Bullish BOS 🚀"
elif latest_close < previous_low:
    signal = "Bearish BOS 🔻"

st.subheader("Market Structure Signal:")
st.write(signal)

# Plot Chart
fig, ax = plt.subplots(figsize=(10,5))
ax.plot(data['Close'], label="Close Price")
ax.scatter(data.index, data['Swing_High'], color='red')
ax.scatter(data.index, data['Swing_Low'], color='green')
ax.legend()

st.pyplot(fig)

