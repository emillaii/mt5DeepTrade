import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping
from sklearn.preprocessing import MinMaxScaler

print("Num GPUs Available:", len(tf.config.experimental.list_physical_devices('GPU')))

# Set GPU 2 (Index 1, since GPU indexing starts from 0)
gpus = tf.config.experimental.list_physical_devices('GPU')

if gpus:
    try:
        tf.config.experimental.set_visible_devices(gpus[1], 'GPU')
        tf.config.experimental.set_memory_growth(gpus[1], True)
        print("Using GPU 2:", gpus[1])
    except RuntimeError as e:
        print(e)

# Load dataset
df = pd.read_csv("data/EURUSD_M15.csv")

# Convert Date and Time into a datetime format
df['Datetime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'])
df.set_index('Datetime', inplace=True)

# Drop unnecessary columns
df.drop(columns=['Date', 'Time'], inplace=True)

# Use 'Close' and 'Tick volume' as input features
data = df[['Close', 'Tick volume']].copy()

# Normalize data with separate scalers
scaler_close = MinMaxScaler(feature_range=(0, 1))
scaler_volume = MinMaxScaler(feature_range=(0, 1))

scaler_close.fit(data[['Close']])
scaler_volume.fit(data[['Tick volume']])

data_scaled = np.hstack((
    scaler_close.transform(data[['Close']]),
    scaler_volume.transform(data[['Tick volume']])
))

# Function to create sequences for LSTM input
def create_sequences(data, seq_length=50):
    X, y = [], []
    for i in range(len(data) - seq_length):
        X.append(data[i:i+seq_length])
        y.append(data[i+seq_length, 0])  # Predicting Close price only
    return np.array(X), np.array(y)

# Define sequence length (lookback window)
seq_length = 50

# Create sequences
X, y = create_sequences(data_scaled, seq_length)

# Train-test split (Manual, to maintain time order)
split_index = int(len(X) * 0.8)
X_train, X_test = X[:split_index], X[split_index:]
y_train, y_test = y[:split_index], y[split_index:]

# Build LSTM model
model = Sequential([
    LSTM(50, return_sequences=True, input_shape=(seq_length, 2)),
    Dropout(0.2),
    LSTM(50, return_sequences=False),
    Dropout(0.2),
    Dense(25, activation='relu'),
    Dense(1)
])

# Compile the model
model.compile(optimizer='adam', loss='mean_squared_error')

# Train with EarlyStopping
early_stopping = EarlyStopping(monitor='val_loss', patience=3, restore_best_weights=True)
history = model.fit(X_train, y_train, epochs=5, batch_size=32, validation_data=(X_test, y_test), callbacks=[early_stopping])

# Save trained model
model.save("lstm_trend_model.h5")
print("Model saved successfully!")

# Plot training loss
plt.figure(figsize=(12, 6))
plt.plot(history.history['loss'], label='Train Loss')
plt.plot(history.history['val_loss'], label='Validation Loss')
plt.xlabel('Epochs')
plt.ylabel('Loss')
plt.legend()
plt.title('LSTM Training Loss')
plt.show()

# --------- PREDICTIONS & ACTUAL PRICE PLOT ---------

# Make predictions
y_pred = model.predict(X_test)

# Convert predictions and actual values back to original scale (Close Price only)
y_pred_actual = scaler_close.inverse_transform(y_pred)
y_test_actual = scaler_close.inverse_transform(y_test.reshape(-1, 1))

# Plot actual vs. predicted close prices
plt.figure(figsize=(12, 6))
plt.plot(y_test_actual, label='Actual Close Price', color='green', linestyle='-')
plt.plot(y_pred_actual, label='Predicted Close Price', color='blue', linestyle='dashed')
plt.xlabel('Time Steps')
plt.ylabel('Close Price')
plt.title('LSTM Prediction vs Actual Close Prices')
plt.legend()
plt.grid()
plt.show()
