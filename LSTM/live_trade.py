import pandas as pd
import talib
import matplotlib.pyplot as plt
import matplotlib.animation as animation

DATA_FILE = "realtime_ticks.csv"
LOG_FILE = "trade_signals_log.csv"  # File to store Buy/Sell signals

# Trading Variables
initial_lot_size = 0.01
lot_multiplier = [2, 2, 2]
pips_gain_for_increase = 100
entry_price = 0
current_lot_size = initial_lot_size
total_trade_lot = 0
position_open = False
is_position_long = None # True for long , False for short
buy_position = []
# Initialize plot
fig, ax = plt.subplots(3, 1, figsize=(12, 8), sharex=True)

def execute_trade(lot_size, isBuy, x_pos):
    """Simulate executing a trade."""
    global total_trade_lot, buy_position
    print(f"Executing trade at {lot_size} lots. {'Buy' if isBuy else 'Sell'} x_pos: {x_pos}")
    total_trade_lot += lot_size
    print(f"Total trade lot : {total_trade_lot}")
    buy_position.append(x_pos)

def close_trade():
    """Simulate closing all trades."""
    global position_open, entry_price, current_lot_size, total_trade_lot
    print(f"Closing all positions. {'Long' if is_position_long else 'Short'} Lot Size: {total_trade_lot}")
    position_open = False
    entry_price = 0 
    current_lot_size = 0.01
    total_trade_lot = 0

def animate(i):
    global entry_price, position_open, is_position_long, current_lot_size, total_trade_lot

    """Fetch latest data and update the plot dynamically."""
    df = pd.read_csv(DATA_FILE)

    # Convert Datetime column
    df["Datetime"] = pd.to_datetime(df["Datetime"])
    df = df.tail(500)  # Keep latest 500 rows for performance

    # Ensure enough data for indicators
    if len(df) >= 50:
        df['SMA_10'] = talib.SMA(df['Close'], timeperiod=10)
        df['SMA_50'] = talib.SMA(df['Close'], timeperiod=50)
        df['EMA_10'] = talib.EMA(df['Close'], timeperiod=10)
        macd, signal, hist = talib.MACD(df['Close'], fastperiod=12, slowperiod=26, signalperiod=9)
        df['MACD'] = macd
        df['MACD_Signal'] = signal
        df['MACD_Hist'] = hist

        df["Distance_SMA50_EMA10"] = -(df["SMA_50"] - df["EMA_10"])

        # Identify Buy and Sell signals
        df["Buy_Signal"] = (df["Distance_SMA50_EMA10"].shift(1) < 0) & (df["Distance_SMA50_EMA10"] > 0)
        df["Sell_Signal"] = (df["Distance_SMA50_EMA10"].shift(1) > 0) & (df["Distance_SMA50_EMA10"] < 0)

        # Log Buy/Sell signals
        trade_signals = df[df["Buy_Signal"] | df["Sell_Signal"]][["Datetime", "Close", "Buy_Signal", "Sell_Signal"]]
        if not trade_signals.empty:
            trade_signals.to_csv(LOG_FILE, mode='a', header=not pd.io.common.file_exists(LOG_FILE), index=False)

        # Handle trading logic
        if df["Buy_Signal"].iloc[-1] and not position_open:
            execute_trade(initial_lot_size, True, df.index[-1])
            entry_price = df["Close"].iloc[-1]
            position_open = True
            is_position_long = True
            current_lot_size = initial_lot_size
        
        # elif df["Sell_Signal"].iloc[-1] and not position_open:
        #     execute_trade(initial_lot_size, False)
        #     entry_price = df["Close"].iloc[-1]
        #     position_open = True
        #     is_position_long = False
        #     current_lot_size = initial_lot_size
        
        if position_open:
            if (is_position_long and df["Sell_Signal"].iloc[-1]) or (not is_position_long and df["Buy_Signal"].iloc[-1]):
                close_trade()

        current_close = df["Close"].iloc[-1]
        #initialize the entry price 
        if (entry_price == 0):
            entry_price = current_close
        diff_in_pips = (current_close - entry_price)*100000
        
        # Trading logic 
        # Check if the position should be added to based on pips gain

        if entry_price is not None and position_open and (diff_in_pips >= pips_gain_for_increase):
            new_lot = current_lot_size * 2
            execute_trade(new_lot, is_position_long, df.index[-1])
            current_lot_size += new_lot
            entry_price = df["Close"].iloc[-1]  # Update entry price to new average if necessary

    else:
        print(f"Waiting for more data... {len(df)}/50 rows available.")
        return  # Skip this frame if not enough data

    ax[0].clear()
    ax[1].clear()
    ax[2].clear()

    # **Price Chart with SMA & EMA**
    ax[0].plot(df.index, df["Close"], label="Close Price", color="black", linewidth=1)
    if "SMA_10" in df.columns:
        ax[0].plot(df.index, df["SMA_10"], label="SMA 10", color="blue", linestyle="dashed")
    if "SMA_50" in df.columns:
        ax[0].plot(df.index, df["SMA_50"], label="SMA 50", color="red", linestyle="dotted")
    if "EMA_10" in df.columns:
        ax[0].plot(df.index, df["EMA_10"], label="EMA 10", color="green", linestyle="dashdot")

    # **Vertical Lines Every 500 Ticks**
    for tick in range(0, len(df), 49):
        ax[0].axvline(x=df.index[tick], color='purple', linestyle='dashed', linewidth=1, alpha=0.8)
        ax[0].text(df.index[tick], df["SMA_10"].min(), df["Datetime"].iloc[tick].strftime('%H:%M:%S'),
           rotation=0, fontsize=6, color='white', ha='right', va='top', bbox=dict(facecolor='purple', alpha=0.5))
        ax[1].axvline(x=df.index[tick], color='purple', linestyle='dashed', linewidth=1, alpha=0.8)
        ax[2].axvline(x=df.index[tick], color='purple', linestyle='dashed', linewidth=1, alpha=0.8)
        

    # Draw the buy position
    for index in buy_position:
        if index in df.index:
            ax[0].axvline(x=index, color='green', linestyle='dashed', linewidth=1, alpha=0.8)
            #ax[0].scatter(index, df.loc[index, "Close"], color='gold', label='Buy Positions', marker='^', s=100)

    ax[0].set_title("Price with SMA & EMA")
    ax[0].legend()
    ax[0].grid()

    # **MACD Chart**
    ax[1].plot(df.index, df["MACD"], label="MACD", color="blue")
    ax[1].plot(df.index, df["MACD_Signal"], label="Signal Line", color="red", linestyle="dashed")

    ax[1].bar(df.index, df["MACD_Hist"].where(df["MACD_Hist"] >= 0), color="green", alpha=0.6, width=0.005, label="MACD Positive")
    ax[1].bar(df.index, df["MACD_Hist"].where(df["MACD_Hist"] < 0), color="red", alpha=0.6, width=0.005, label="MACD Negative")

    ax[1].set_title("MACD Indicator")
    ax[1].legend()
    ax[1].grid()

    # **Distance Between SMA_50 and EMA_10**
    ax[2].plot(df.index, df["Distance_SMA50_EMA10"], label="Distance (SMA50 - EMA10)", color="purple", linewidth=1.5)
    ax[2].fill_between(df.index, df["Distance_SMA50_EMA10"], color="purple", alpha=0.3)  # Shaded area for better visibility
    ax[2].set_title("Distance Between SMA_50 and EMA_10")

    # Plot the buy / sell entry 
    buy_signals = df[df["Buy_Signal"]]
    sell_signals = df[df["Sell_Signal"]]
    buy_y = [0] * len(buy_signals)  # Creates a list of zeros with the same length as buy_signals
    sell_y = [0] * len(sell_signals)
    ax[2].scatter(buy_signals.index, buy_y, color='green', label='Buy Signal', marker='^', s=100)
    ax[2].scatter(sell_signals.index, sell_y, color='red', label='Sell Signal', marker='v', s=100)
        
    ax[2].legend()
    ax[2].grid()

    plt.xticks(rotation=45)


# **Run Live Animation**
ani = animation.FuncAnimation(fig, animate, interval=300)  # Update every second
plt.show()
