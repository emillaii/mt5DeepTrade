import pandas as pd
import matplotlib.pyplot as plt
import io
from PIL import Image

def analyze_deals(deals):
    # Filter out non-trade entries (like the initial balance or summary)
    trades = [row for row in deals if len(row) > 1 and row[2] != 'balance']

    df = pd.DataFrame(trades[1:], columns=trades[0])
    # Convert relevant columns to numeric types
    df['Volume'] = pd.to_numeric(df['Volume'], errors='coerce')
    df['Profit'] = df['Profit'].str.replace(' ', '', regex=False)
    df['Profit'] = pd.to_numeric(df['Profit'], errors='coerce')

    # Calculate total volume traded
    total_volume = df['Volume'].sum()

    # Calculate win rate:
    # - A trade is considered a win if Profit is positive
    wins = df[(df['Profit'] > 0) & (df['Direction'] == 'out')] 
    total_wins = len(wins)
    total_trades = len(df[df['Direction'] == 'out'])

    win_rate = total_wins / total_trades if total_trades > 0 else 0

    # Calculate volume-weighted win rate
    win_volume = wins['Volume'].sum()

    sum_of_profit = df[(df['Direction'] == 'out')]['Profit'].sum()

    result = f"Total Trades: {total_trades}\n"
    result += f"Total Wins: {total_wins}\n"
    result += f"Win Rate: {win_rate:.2%}\n"
    result += f"Total Volume: {total_volume:.2f}\n"
    result += f"Win Volume: {win_volume:.2f}\n"
    result += f"Total Profit: {sum_of_profit:.2f}\n"

    # Additional analysis for win rate per volume size per symbol
    result += "\nWin Rate per Volume Size per Symbol:\n"

    # Group by Symbol and Volume to calculate win rates
    grouped = df[df['Direction'] == 'out'].groupby(['Symbol', 'Volume'])

    plot_data = []
    for (symbol, volume), group in grouped:
        symbol_wins = group[group['Profit'] > 0]
        win_count = len(symbol_wins)
        total_count = len(group)
        symbol_win_rate = win_count / total_count if total_count > 0 else 0
        sum_of_profit = group['Profit'].sum()
        # Calculate expected value of profit
        expected_value = (symbol_win_rate * group[group['Profit'] > 0]['Profit'].mean()) - \
                     ((1 - symbol_win_rate) * group[group['Profit'] <= 0]['Profit'].abs().mean()) if total_count > 0 else 0

        
        result += f"Symbol: {symbol}, Volume: {volume}\n"
        result += f"  - Trades: {total_count}\n"
        result += f"  - Wins: {win_count}\n"
        result += f"  - Win Rate: {symbol_win_rate:.2%}\n"
        result += f"  - Profit: {sum_of_profit:.2f}\n"
        result += f"  - Expected Value of Profit: {expected_value:.2f}\n"
        result += "\n"
        
        plot_data.append({
            'Symbol': symbol,
            'Volume': volume,
            'Win Rate': symbol_win_rate,
            'Expected Value': expected_value 
        })

    # Generate plot
    plot_df = pd.DataFrame(plot_data)
    fig, ax1 = plt.subplots(figsize=(10, 6))

    # Plot Win Rate
    for symbol, group in plot_df.groupby('Symbol'):
        ax1.scatter(group['Volume'], group['Win Rate'], label=f'Win Rate {symbol}')
    ax1.set_xlabel('Volume')
    ax1.set_ylabel('Win Rate', color='b')
    ax1.tick_params(axis='y', labelcolor='b')
    ax1.set_title('Win Rate & Expected Value vs Volume per Symbol')
    ax1.legend(loc='upper left')

    # Create another y-axis for Expected Value
    ax2 = ax1.twinx()  
    for symbol, group in plot_df.groupby('Symbol'):
        ax2.scatter(group['Volume'], group['Expected Value'], color='r', marker='x', label=f'Expected Value {symbol}')
    ax2.set_ylabel('Expected Value', color='r')
    ax2.tick_params(axis='y', labelcolor='r')
    ax2.legend(loc='upper right')


    # Convert plot to bytes for Gradio
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_image = Image.open(img)

    return result, plot_image