import streamlit as st
from dotenv import load_dotenv
import os
import mysql.connector
import getpass
from PIL import Image

load_dotenv()

st.set_page_config(
    page_title="Kanoon ki Pehchaan",
    page_icon="⚖",
    layout="wide",
    initial_sidebar_state="expanded"
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

username = st.session_state.get('username', getpass.getuser())
st.markdown('<div class="main-header">', unsafe_allow_html=True)
st.markdown('<div class="flag-stripe"></div>', unsafe_allow_html=True)
st.title(f"{username}'s Dashboard")
st.markdown('</div>', unsafe_allow_html=True)

st.markdown("""
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.7.2/css/all.min.css" integrity="sha512-Evv84Mr4kqVGRNSgIGL/F/aIDqQb7xQ2vcrdIwxfjThSH8CSR7PBEakCr51Ck+w+/U6swU2Im1vVX0SVk9ABhg==" crossorigin="anonymous" referrerpolicy="no-referrer" />
""", unsafe_allow_html=True)

conn = get_db_connection()
cursor = conn.cursor(dictionary=True)
cursor.execute("SELECT profile_pic_url FROM users WHERE name = %s", (username,))
users = cursor.fetchall()
cursor.close()
conn.close()

st.markdown('<div class="card animate-fadeIn">', unsafe_allow_html=True)
for user in users:
    if os.path.exists(user["profile_pic_url"]):
        st.image(user["profile_pic_url"], width=150, caption="Profile Picture")
    st.markdown("---")

st.header("Your Profile")
conn = get_db_connection()
cursor = conn.cursor(dictionary=True)
cursor.execute("SELECT * FROM users WHERE name = %s", (username,))
users = cursor.fetchall()
cursor.close()
conn.close()

for user in users:
    st.subheader(user["name"])
    st.text(f"Degree: {user['degree']}")
    st.text(f"College: {user['college']}")
    st.text(f"Qualifications: {user['myQualifications']}")
    st.text(f"Phone Number: {user['Phone_No']}")
    st.text(f"Social Media: {user['social_media']}")
    
st.markdown("""
    <div style="text-align: center;">
        <a href="/editlawyer" style="color: #ffffff; text-decoration: none;">
            <i class="fa-solid fa-user-pen"></i> Edit Details
        </a>
    </div>
""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
st.markdown('<div class="footer">Your Lawyer Profile</div>', unsafe_allow_html=True)