import streamlit as st
from groq import Groq
import google.generativeai as genai

# Corrected Page Config (No repeated arguments)
st.set_page_config(
    page_title="ARISE AI", 
    page_icon="✨", 
    layout="wide"
)

# Elite Styling: Black Chancery Bold Italic & Times Roman
st.markdown("""
    <style>
    @import url('https://fonts.cdnfonts.com/css/black-chancery');
    
    .arise-title {
        font-family: 'Black Chancery', cursive;
        font-size: 6rem; font-weight: bold; font-style: italic;
        text-align: center; color: #5E767E; text-transform: uppercase;
        margin-top: -70px;
    }
    html, body, [class*="st-"], .stMarkdown, p {
        font-family: "Times New Roman", Times, serif !important;
    }
    [data-testid="stSidebar"] { background-color: #1e1f20; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<div class='arise-title'>ARISE</div>", unsafe_allow_html=True)
# ... rest of your logic ...
