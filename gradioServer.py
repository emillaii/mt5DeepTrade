import gradio as gr
from bs4 import BeautifulSoup
import chardet
import pandas as pd

def analyze_html(file_path):
    try:
        # Read file in binary mode to detect encoding
        with open(file_path, "rb") as f:
            raw_data = f.read()
            detected_encoding = chardet.detect(raw_data)["encoding"]
        
        if not detected_encoding:
            return "Error: Unable to detect file encoding."
        
        # Read the file using detected encoding
        with open(file_path, "r", encoding=detected_encoding, errors="replace") as f:
            html_content = f.read()

        # Parse HTML content
        soup = BeautifulSoup(html_content, "html.parser")

        # Extract title
        title = soup.title.string.strip() if soup.title else "No title found"

        # Extract headings (h1 to h6)
        headings = {f"h{i}": [h.get_text(strip=True) for h in soup.find_all(f"h{i}")] for i in range(1, 7)}

        # Extract links
        links = [a["href"] for a in soup.find_all("a", href=True)]

        # Extract text content
        text_content = soup.get_text(separator="\n", strip=True)

        # Extract tables
        tables = soup.find_all('table')

        summary = []
        orders = []
        deals = []
        for idx, table in enumerate(tables, 1):
            rows = []
            foundStartPoint = False
            isOrders = False
            isDeals = False
            for row in table.find_all('tr'):
                columns = [col.get_text(strip=True) for col in row.find_all(['th','td'])]
                columns = [col for col in columns if col != '']
                if idx == 1: 
                    if foundStartPoint:
                        for i in range(0, len(columns), 2):
                            if i + 1 < len(columns):
                                col_data = [columns[i], columns[i + 1]]
                                rows.append(col_data)
                            else:
                                col_data = [columns[i]]
                                #rows.append(col_data)
                    elif columns and columns[0] == "Results":  # Ensure 'Results' is the first column if present
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
            
            if rows:  # Only append if there's data in rows
                summary.append(rows)

        # Prepare the result
        result = f"**Title:** {title}\n\n"
        for h_level, h_texts in headings.items():
            if h_texts:
                result += f"**{h_level.upper()} Headings:** {', '.join(h_texts)}\n\n"
        result += f"**Links:** {', '.join(links) if links else 'No links found'}\n\n"
        if summary and len(summary) > 0:
            return result, summary[0], orders, deals

        return result, [], orders, deals

    except Exception as e:
        return f"Error processing file: {str(e)}"

def main():
    with gr.Blocks() as demo:
        gr.Markdown("# HTML Analysis & Data Display")
        
        with gr.Tab("HTML File Analyzer"):
            with gr.Row():
                with gr.Column(scale=1):
                    html_file_input = gr.File(label="Upload HTML File")
                    html_analyze_btn = gr.Button("Analyze")
                with gr.Column(scale=2):
                    html_output = gr.Textbox(label="Analysis Results")

            with gr.Row():
                with gr.Column(scale=1):
                    summary = gr.DataFrame(label="Summary")
                
            with gr.Row():
                with gr.Column(scale=1):
                    orders = gr.DataFrame(label="Orders")

            with gr.Row():
                with gr.Column(scale=1):
                    deals = gr.DataFrame(label="Deals")
            
            html_analyze_btn.click(analyze_html, inputs=[html_file_input], outputs=[html_output, summary, orders, deals])

    demo.launch()

if __name__ == "__main__":
    main()