from flask import Flask, request, jsonify
import pandas as pd
import os

# Initialize Flask app
app = Flask(__name__)

# File to store real-time tick data
DATA_FILE = "realtime_ticks.csv"

# Ensure file exists with headers
if not os.path.exists(DATA_FILE):
    pd.DataFrame(columns=["Datetime", "Open", "High", "Low", "Close", "Tick Volume"]).to_csv(DATA_FILE, index=False)

@app.route('/ticks', methods=['POST'])
def receive_tick():
    tick = request.json
    print("Received Data:", tick)

    # Convert tick data into DataFrame
    new_row = pd.DataFrame([{
        "Datetime": tick["timestamp"],
        "Open": tick["open"],
        "High": tick["high"],
        "Low": tick["low"],
        "Close": tick["close"],
        "Tick Volume": tick["volume"]
    }])

    # Append tick data to CSV file
    new_row.to_csv(DATA_FILE, mode="a", header=False, index=False)

    return jsonify({"message": "Tick received", "tick": tick})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
