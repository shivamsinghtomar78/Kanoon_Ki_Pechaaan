import streamlit as st
import firebase_admin
from firebase_admin import credentials, auth
import json
import requests
from dotenv import load_dotenv
import os
import logging
from pathlib import Path
import mysql.connector

logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()
api_key = os.getenv("FIREBASE_API_KEY")

if not api_key:
    logger.error("Firebase API key not found.")
    st.error("Configuration error: Firebase API key not available.")

def init_firebase():
    try:
        if not firebase_admin._apps:
            cred_file = "kanoon-ki-pehchaan-6ff0ed4a9c13.json"
            if not Path(cred_file).exists():
                logger.error(f"Firebase credential file not found: {cred_file}")
                st.error("Configuration error: Firebase credentials not available.")
                return False
            cred = credentials.Certificate(cred_file)
            firebase_admin.initialize_app(cred)
            logger.info("Firebase initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize Firebase: {e}")
        st.error("An error occurred during initialization.")
        return False

st.set_page_config(
    page_title="Kanoon ki Pehchaan",
    page_icon="⚖",
    layout="centered",
    initial_sidebar_state="collapsed"
)

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="0819",
        database="lawyers"
    )

def local_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700&family=Orbitron:wght@400;700&display=swap');
        body {
            font-family: 'Montserrat', sans-serif;
            background: linear-gradient(135deg, #0A0A0A 0%, #1A1A1A 100%);
            color: #FFFFFF;
        }
        h1, h2, h3 { font-family: 'Orbitron', sans-serif; }
        .main-header {
            position: fixed;
            top: 0;
            width: 100%;
            text-align: center;
            padding: 1.5rem;
            background: rgba(0, 0, 0, 0.8);
            border-bottom: 2px solid #00FFFF;
            box-shadow: 0 0 15px #00FFFF;
            animation: slideInLeft 0.5s ease-in;
            z-index: 1000;
        }
        .flag-stripe {
            height: 6px;
            background: linear-gradient(90deg, #FF00FF 33%, #00FFFF 66%, #00FF00 100%);
            animation: slideInLeft 0.5s ease-in;
        }
        .stTextInput > div > input, .stTextArea > div > textarea {
            border-radius: 20px;
            padding: 0.8rem 2rem;
            background: rgba(0, 0, 0, 0.7);
            border: 2px solid #00FFFF;
            color: #FFFFFF;
            transition: all 0.3s ease;
        }
        .stTextInput > div > input:focus, .stTextArea > div > textarea:focus {
            border-color: #FF00FF;
            box-shadow: 0 0 15px #FF00FF;
        }
        .stButton > button {
            border-radius: 20px;
            padding: 0.6rem 1.5rem;
            background: linear-gradient(135deg, #00FFFF, #FF00FF);
            color: #000000;
            border: none;
            font-weight: bold;
            text-transform: uppercase;
            box-shadow: 0 0 10px #00FFFF;
            transition: all 0.3s ease;
        }
        .stButton > button:hover {
            transform: scale(1.05);
            box-shadow: 0 0 20px #FF00FF;
        }
        .card {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            border: 1px solid rgba(0, 255, 255, 0.3);
            padding: 1.5rem;
            margin: 1rem 0;
            transition: all 0.3s ease;
        }
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 0 20px #FF00FF;
        }
        .footer {
            position: fixed;
            bottom: 0;
            width: 100%;
            background: rgba(0, 0, 0, 0.9);
            padding: 1rem;
            text-align: center;
            border-top: 2px solid #00FFFF;
            animation: fadeIn 0.5s ease-in;
        }
        @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
        @keyframes slideInLeft { from { transform: translateX(-100%); } to { transform: translateX(0); } }
    </style>
    """, unsafe_allow_html=True)

local_css()

st.markdown('<div class="main-header">', unsafe_allow_html=True)
st.markdown('<div class="flag-stripe"></div>', unsafe_allow_html=True)
st.title("⚖ Kanoon ki Pehchaan")
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="card animate-fadeIn">', unsafe_allow_html=True)
case_details = st.text_area("Enter your case details")
conn = get_db_connection()
cursor = conn.cursor(dictionary=True)
cursor.execute("SELECT * FROM users")
users = cursor.fetchall()
cursor.close()
conn.close()

if st.button("Submit"):
    st.subheader("Here is a list of lawyers for you:")
    for user in users:
        col1, col2 = st.columns([1, 3])
        with col1:
            if os.path.exists(user["profile_pic_url"]):
                st.image(user["profile_pic_url"], width=150, caption="Profile Picture")
        with col2:
            st.text(f"Name: {user['name']}")
            st.text(f"Degree: {user['degree']}")
            st.text(f"College: {user['college']}")
            st.text(f"Qualifications: {user['myQualifications']}")
            st.text(f"Phone Number: {user['Phone_No']}")
            st.text(f"Social Media: {user['social_media']}")
            st.markdown("---")
st.markdown('</div>', unsafe_allow_html=True)
st.markdown('<div class="footer">Connect with Lawyers</div>', unsafe_allow_html=True)