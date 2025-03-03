import numpy as np
import pandas as pd
import tensorflow as tf
import matplotlib.pyplot as plt
from tensorflow.keras.models import load_model
from sklearn.preprocessing import MinMaxScaler

# File paths
model_path = "lstm_trend_model.h5"  
data_path = "data/test.csv"

# Load the trained LSTM model
model = load_model(model_path)

# Load dataset
df = pd.read_csv(data_path)

# Convert Date and Time into a datetime format
if 'Date' in df.columns and 'Time' in df.columns:
    df['Datetime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'])
    df.set_index('Datetime', inplace=True)

# Drop unnecessary columns
df.drop(columns=['Date', 'Time'], inplace=True)

# Use 'Close' and 'Tick volume' as input features
data = df[['Close', 'Tick volume']].copy()

# Normalize data (use same scalers as training)
scaler_close = MinMaxScaler(feature_range=(0, 1))
scaler_volume = MinMaxScaler(feature_range=(0, 1))

data_scaled = np.hstack((
    scaler_close.fit_transform(data[['Close']]),  
    scaler_volume.fit_transform(data[['Tick volume']])
))

# Define sequence length (lookback window)
seq_length = 50
num_predictions = 20  # Predict next 20 closing prices

# Function to create sequences for LSTM input
def create_sequences(data, seq_length=50):
    X = []
    for i in range(len(data) - seq_length):
        X.append(data[i:i+seq_length])
    return np.array(X)

# Create sequences (Only take the last available sequence)
X_test = create_sequences(data_scaled, seq_length)[-1:]

# Predicting Next 20 Close Prices
predicted_prices = []
last_seq = X_test  # Start with last observed sequence

for _ in range(num_predictions):
    # Predict the next price
    predicted_price_scaled = model.predict(last_seq)

    # Convert back to actual price
    predicted_price = scaler_close.inverse_transform(predicted_price_scaled.reshape(-1, 1))[0][0]
    predicted_prices.append(predicted_price)

    # Reuse the last known 'Tick Volume' value
    last_tick_volume = last_seq[:, -1, 1]  # Extract the last known tick volume

    # Combine the predicted Close price with the last Tick Volume
    predicted_combined = np.array([[predicted_price_scaled[0, 0], last_tick_volume[0]]]).reshape(1, 1, 2)

    # Append to sequence
    new_seq = np.append(last_seq[:, 1:, :], predicted_combined, axis=1)
    last_seq = new_seq

# Extract last 50 actual closing prices for context
past_prices = data.iloc[-seq_length:]['Close'].values

# Generate time steps for past and future predictions
past_time_steps = list(range(-seq_length, 0))  # Past 50 time steps
future_time_steps = list(range(1, num_predictions + 1))  # Next 20 predicted steps

# Plot past and predicted prices on the timeline
plt.figure(figsize=(14, 6))

# Plot past actual prices
plt.plot(past_time_steps, past_prices, marker='o', linestyle='-', color='green', label="Past Actual Prices")

# Plot future predicted prices
plt.plot(future_time_steps, predicted_prices, marker='o', linestyle='dashed', color='blue', label="Predicted Future Prices")

# Vertical line to separate actual and predicted values
plt.axvline(x=0, color='red', linestyle='--', label="Prediction Start Point")

# Labels and title
plt.xlabel("Time Steps (T)")
plt.ylabel("Close Price")
plt.title("LSTM Prediction Timeline: Past & Future Closing Prices")
plt.legend()
plt.grid()

# Show the plot
plt.show()
