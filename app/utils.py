import streamlit as st

def setup_sidebar(logo_path="logo/logo.png"):
    # Inject CSS to fix sidebar width and center the logo
    st.sidebar.markdown(
        """
        <style>
        /* Fix sidebar width to 200px */
        [data-testid="stSidebar"] {
            width: 200px !important;
            padding: 10px;
        }
        /* Center the image in the sidebar */
        [data-testid="stSidebar"] img {
            display: block;
            margin-left: auto;
            margin-right: auto;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    # Display centered logo and title
    st.sidebar.image(logo_path, width=150)
    st.sidebar.markdown("<h2 style='text-align: center;'>My App</h2>", unsafe_allow_html=True)