import numpy as np
import pandas as pd
import tensorflow as tf
import matplotlib.pyplot as plt
from tensorflow.keras.models import load_model
from sklearn.preprocessing import MinMaxScaler

# File paths
model_path = "lstm_trend_model.h5"  
test_data_path = "data/test.csv"  

# Load the trained LSTM model
model = load_model(model_path)

# Load test data
df_real_time = pd.read_csv(test_data_path)

# Convert Date and Time into a datetime format if applicable
if 'Date' in df_real_time.columns and 'Time' in df_real_time.columns:
    df_real_time['Datetime'] = pd.to_datetime(df_real_time['Date'] + ' ' + df_real_time['Time'])
    df_real_time.set_index('Datetime', inplace=True)

# Use only 'Close' price
data = df_real_time[['Close']].copy()

# Normalize data
scaler = MinMaxScaler(feature_range=(0, 1))
data_scaled = scaler.fit_transform(data)

# Sequence length
seq_length = 50

# Extract the last `seq_length` values for prediction
last_seq = np.array(data_scaled[-seq_length:]).reshape(1, seq_length, 1)

# Number of future predictions
num_predictions = 40
predicted_prices = []

# Iteratively predict the next 20 prices
for _ in range(num_predictions):
    # Predict next price
    predicted_price_scaled = model.predict(last_seq)

    # Convert back to actual price
    predicted_price = scaler.inverse_transform(predicted_price_scaled.reshape(-1, 1))[0][0]
    predicted_prices.append(predicted_price)

    # Append prediction to the sequence and remove the oldest value
    new_seq = np.append(last_seq[:, 1:, :], predicted_price_scaled.reshape(1, 1, 1), axis=1)
    last_seq = new_seq

# Get past 50 actual closing prices
past_prices = data.iloc[-seq_length:].values.flatten()

# Generate time steps for past and future predictions
past_time_steps = list(range(-seq_length, 0))  
future_time_steps = list(range(1, num_predictions + 1))  

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
plt.ylabel("Closing Price")
plt.title("LSTM Prediction Timeline: Past & Future Closing Prices")
plt.legend()
plt.grid()

# Show the plot
plt.show()
