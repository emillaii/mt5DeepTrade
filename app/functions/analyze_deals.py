import streamlit as st
from bs4 import BeautifulSoup
import chardet
import pandas as pd
import io

def analyze_deals(deals):
    trades = [row for row in deals if len(row) > 1 and row[2] != 'balance']
    df = pd.DataFrame(trades[1:], columns=trades[0])
    df['Volume'] = pd.to_numeric(df['Volume'], errors='coerce')
    df['Profit'] = df['Profit'].str.replace(' ', '', regex=False)
    df['Profit'] = pd.to_numeric(df['Profit'], errors='coerce')

    total_volume = df['Volume'].sum()
    wins = df[(df['Profit'] > 0) & (df['Direction'] == 'out')]
    total_wins = len(wins)
    total_trades = len(df[df['Direction'] == 'out'])
    win_rate = total_wins / total_trades if total_trades > 0 else 0
    win_volume = wins['Volume'].sum()
    sum_of_profit = df[df['Direction'] == 'out']['Profit'].sum()

    result = f"Total Trades: {total_trades}\\n"
    result += f"Total Wins: {total_wins}\\n"
    result += f"Win Rate: {win_rate:.2%}\\n"
    result += f"Total Volume: {total_volume:.2f}\\n"
    result += f"Win Volume: {win_volume:.2f}\\n"
    result += f"Total Profit: {sum_of_profit:.2f}\\n"

    st.subheader("Deals Data Table")
    st.dataframe(df)

    plot_data = []
    grouped = df[df['Direction'] == 'out'].groupby(['Symbol', 'Volume'])
    for (symbol, volume), group in grouped:
        symbol_wins = group[group['Profit'] > 0]
        win_count = len(symbol_wins)
        total_count = len(group)
        symbol_win_rate = win_count / total_count if total_count > 0 else 0
        sum_of_profit = group['Profit'].sum()
        expected_value = (symbol_win_rate * group[group['Profit'] > 0]['Profit'].mean()) - \
                         ((1 - symbol_win_rate) * group[group['Profit'] <= 0]['Profit'].abs().mean()) if total_count > 0 else 0

        result += f"Symbol: {symbol}, Volume: {volume}\\n"
        result += f"  - Trades: {total_count}\\n  - Wins: {win_count}\\n  - Win Rate: {symbol_win_rate:.2%}\\n  - Profit: {sum_of_profit:.2f}\\n  - Expected Value of Profit: {expected_value:.2f}\\n\\n"

        plot_data.append({
            'Symbol': symbol,
            'Volume': volume,
            'Win Rate': symbol_win_rate,
            'Trades': total_count,
            'Wins': win_count,
            'Profit': sum_of_profit,
            'Expected Value': expected_value
        })

    plot_df = pd.DataFrame(plot_data)
    st.subheader("Win Rate Table")
    st.dataframe(plot_df)

    st.subheader("Win Rate vs Volume per Symbol")
    for symbol, group in plot_df.groupby('Symbol'):
        st.scatter_chart(group.set_index('Volume')[['Win Rate']], height=400)

    return result

def analyze_html(file):
    try:
        raw_data = file.read()
        detected_encoding = chardet.detect(raw_data)["encoding"]
        if not detected_encoding:
            return "Error: Unable to detect file encoding.", [], [], []

        html_content = raw_data.decode(detected_encoding, errors="replace")
        soup = BeautifulSoup(html_content, "html.parser")

        title = soup.title.string.strip() if soup.title else "No title found"
        headings = {f"h{i}": [h.get_text(strip=True) for h in soup.find_all(f"h{i}")] for i in range(1, 7)}
        tables = soup.find_all("table")

        summary, orders, deals = [], [], []
        for idx, table in enumerate(tables, 1):
            rows, foundStartPoint, isOrders, isDeals = [], False, False, False
            for row in table.find_all("tr"):
                columns = [col.get_text(strip=True) for col in row.find_all(["th", "td"])]
                columns = [col for col in columns if col != ""]
                if idx == 1:
                    if foundStartPoint:
                        for i in range(0, len(columns), 2):
                            rows.append(columns[i:i + 2])
                    elif columns and columns[0] == "Results":
                        foundStartPoint = True
                else:
                    if columns and columns[0] == "Orders":
                        isOrders, isDeals = True, False
                        continue
                    elif columns and columns[0] == "Deals":
                        isOrders, isDeals = False, True
                        continue
                    if isOrders:
                        orders.append(columns)
                    elif isDeals:
                        deals.append(columns)
            if rows:
                summary.append(rows)

        result = f"**Title:** {title}\\n\\n"
        for h_level, h_texts in headings.items():
            if h_texts:
                result += f"**{h_level.upper()} Headings:** {', '.join(h_texts)}\\n\\n"
        
        if summary:
            result += analyze_deals(deals)
        
        print("Finish")
        return result, summary[0] if summary else [], orders, deals

    except Exception as e:
        return f"Error processing file: {str(e)}", [], [], []

def main():
    st.title("HTML Analysis & Data Display")

    uploaded_file = st.file_uploader("Upload HTML File", type=["html", "htm"])
    if uploaded_file is not None:
        with st.spinner("Analyzing HTML file..."):
            result, summary, orders, deals = analyze_html(uploaded_file)
            st.markdown(result)

            if summary:
                st.subheader("Summary")
                st.dataframe(summary)

            if orders:
                st.subheader("Orders")
                st.dataframe(orders)

            if deals:
                st.subheader("Deals")
                st.dataframe(deals)

if __name__ == "__main__":
    main()
