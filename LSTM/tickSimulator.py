import time
import requests
import pandas as pd
from datetime import datetime

# API Endpoint (replace with your actual API URL)
API_URL = "http://127.0.0.1:5000/ticks"

# Load CSV File
csv_file = "data/EURUSD_M15.csv"  # Adjust path if needed
df = pd.read_csv(csv_file)

# Rename columns to match expected format
df.columns = ['Date', 'Time', 'Open', 'High', 'Low', 'Close', 'Tick Volume']

# Combine Date & Time into a single datetime column
df['Datetime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'])

# Select only required columns
df = df[['Datetime', 'Open', 'High', 'Low', 'Close', 'Tick Volume']]

# Stream data row by row
def stream_tick_data():
    for _, row in df.iterrows():
        tick_data = {
            "timestamp": row["Datetime"].isoformat(),
            "open": row["Open"],
            "high": row["High"],
            "low": row["Low"],
            "close": row["Close"],
            "volume": row["Tick Volume"]
        }

        print(tick_data)

        # Send data to API
        response = requests.post(API_URL, json=tick_data)

        # Print status
        if response.status_code == 200:
            print(f"✅ Sent: {tick_data}")
        else:
            print(f"❌ Error {response.status_code}: {response.text}")

        time.sleep(0.3)  # Wait 1 second before sending the next row

# Run the stream
if __name__ == "__main__":
    stream_tick_data()
