import pandas as pd
import talib
import matplotlib.pyplot as plt

# Load the dataset
df = pd.read_csv("data/EURUSD_M15.csv")

# Rename columns correctly
df.columns = ['Date', 'Time', 'Open', 'High', 'Low', 'Close', 'Tick Volume']

# Combine 'Date' and 'Time' into a single datetime column
df['Datetime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'])

# Drop original 'Date' and 'Time' columns
df = df[['Datetime', 'Open', 'High', 'Low', 'Close', 'Tick Volume']]

# Calculate indicators
df['SMA_10'] = talib.SMA(df['Close'], timeperiod=10)
df['SMA_50'] = talib.SMA(df['Close'], timeperiod=50)
df['EMA_10'] = talib.EMA(df['Close'], timeperiod=200)
df['RSI'] = talib.RSI(df['Close'], timeperiod=14)

# Bollinger Bands
upper_band, middle_band, lower_band = talib.BBANDS(df['Close'], timeperiod=20)
df['Upper_Band'] = upper_band
df['Middle_Band'] = middle_band
df['Lower_Band'] = lower_band

# MACD
macd, signal, hist = talib.MACD(df['Close'], fastperiod=12, slowperiod=26, signalperiod=9)
df['MACD'] = macd
df['MACD_Signal'] = signal
df['MACD_Hist'] = hist

import matplotlib.dates as mdates
df_subset = df.tail(1000)  # Select last 1000 rows

# Create a figure with two subplots
fig, ax = plt.subplots(2, 1, figsize=(12, 10), sharex=True, gridspec_kw={'height_ratios': [2, 1]})

### **Price Chart with SMA & EMA**
ax[0].plot(df_subset.index, df_subset['Close'], label='Close Price', color='black', linewidth=1)
ax[0].plot(df_subset.index, df_subset['SMA_10'], label='SMA 10', color='blue', linestyle='dashed')
ax[0].plot(df_subset.index, df_subset['SMA_50'], label='SMA 50', color='red', linestyle='dotted')
ax[0].plot(df_subset.index, df_subset['EMA_10'], label='EMA 10', color='green', linestyle='dashdot')

ax[0].set_title('Price with SMA & EMA')
ax[0].set_ylabel('Price')
ax[0].legend()
ax[0].grid()

### **MACD Chart**
positive_hist = df_subset['MACD_Hist'].copy()
negative_hist = df_subset['MACD_Hist'].copy()

positive_hist[positive_hist < 0] = 0  # Keep only positive values
negative_hist[negative_hist > 0] = 0  # Keep only negative values

ax[1].plot(df_subset.index, df_subset['MACD'], label='MACD', color='blue')
ax[1].plot(df_subset.index, df_subset['MACD_Signal'], label='Signal Line', color='red', linestyle='dashed')


# Plot MACD Histogram with different colors
ax[1].bar(df_subset.index, positive_hist, color='green', alpha=0.8, label='MACD Positive')
ax[1].bar(df_subset.index, negative_hist, color='red', alpha=0.8, label='MACD Negative')


ax[1].set_title('MACD Indicator')
ax[1].set_xlabel('Datetime')
ax[1].set_ylabel('MACD Value')
ax[1].legend()
ax[1].grid()

# Improve X-axis date formatting
locator = mdates.AutoDateLocator(minticks=5, maxticks=10) 
ax[1].xaxis.set_major_locator(locator)
# ax[1].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))  # Format as Year-Month-Day Hour:Minute

plt.xticks(rotation=45)  # Rotate labels for readability

# Show the figure
plt.tight_layout()
plt.show()
