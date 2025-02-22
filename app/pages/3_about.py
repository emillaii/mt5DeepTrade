import streamlit as st
from utils import setup_sidebar
setup_sidebar(logo_path="logo/logo.png")

st.title("About Page")
st.write("Welcome to the about page!")