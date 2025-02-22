import streamlit as st
from bs4 import BeautifulSoup
import chardet
from functions.analyze_deals import analyze_deals
from PIL import Image
import io

from utils import setup_sidebar
setup_sidebar(logo_path="logo/logo.png")

def analyze_html(file):
    try:
        # Read file in binary mode to detect encoding
        raw_data = file.read()
        detected_encoding = chardet.detect(raw_data)["encoding"]

        if not detected_encoding:
            return "Error: Unable to detect file encoding.", [], [], [], None

        # Read the file using detected encoding
        html_content = raw_data.decode(detected_encoding, errors="replace")

        # Parse HTML content
        soup = BeautifulSoup(html_content, "html.parser")

        # Extract title
        title = soup.title.string.strip() if soup.title else "No title found"

        # Extract headings (h1 to h6)
        headings = {
            f"h{i}": [h.get_text(strip=True) for h in soup.find_all(f"h{i}")]
            for i in range(1, 7)
        }

        # Extract links
        links = [a["href"] for a in soup.find_all("a", href=True)]

        # Extract tables
        tables = soup.find_all("table")

        summary = []
        orders = []
        deals = []
        for idx, table in enumerate(tables, 1):
            rows = []
            foundStartPoint = False
            isOrders = False
            isDeals = False
            for row in table.find_all("tr"):
                columns = [
                    col.get_text(strip=True) for col in row.find_all(["th", "td"])
                ]
                columns = [col for col in columns if col != ""]
                if idx == 1:
                    if foundStartPoint:
                        for i in range(0, len(columns), 2):
                            if i + 1 < len(columns):
                                col_data = [columns[i], columns[i + 1]]
                                rows.append(col_data)
                            else:
                                col_data = [columns[i]]
                    elif columns and columns[0] == "Results":
                        foundStartPoint = True
                else:
                    if columns and columns[0] == "Orders":
                        isOrders = True
                        isDeals = False
                        continue
                    elif columns and columns[0] == "Deals":
                        isOrders = False
                        isDeals = True
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
            deal_result = analyze_deals(deals)
            result += deal_result

        return result, summary[0] if summary else [], orders, deals

    except Exception as e:
        return f"Error processing file: {str(e)}", [], [], [], None

# Page content
st.title("HTML Analysis & Data Display")

uploaded_file = st.file_uploader("Upload HTML File", type=["html", "htm"])
if uploaded_file is not None:
    with st.spinner("Analyzing HTML file..."):
        result, summary, orders, deals = analyze_html(uploaded_file)
        
        if summary:
            st.subheader("Summary")
            st.dataframe(summary)

        if orders:
            st.subheader("Orders")
            st.dataframe(orders)

        if deals:
            st.subheader("Deals")
            st.dataframe(deals)