import streamlit as st
from utils import setup_sidebar

setup_sidebar(logo_path="logo/logo.png")

# Main content (optional, can be minimal)
st.title("Welcome to My App")
st.write("Use the sidebar to navigate between pages.")