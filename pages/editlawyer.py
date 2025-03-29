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
    try:
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="0819",
            database="lawyers"
        )
    except mysql.connector.Error as err:
        logger.error(f"Database connection error: {err}")
        st.error("Could not connect to database.")
        return None

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
        .stTextInput > div > input {
            border-radius: 20px;
            padding: 0.8rem 2rem;
            background: rgba(0, 0, 0, 0.7);
            border: 2px solid #00FFFF;
            color: #FFFFFF;
            transition: all 0.3s ease;
        }
        .stTextInput > div > input:focus {
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

if not st.session_state.get('authenticated', False):
    st.warning("You must be logged in to edit your profile.")
    st.page_link("Homepage.py", label="Login here", icon="🔑")
else:
    username = st.session_state.get('username', '')
    st.markdown('<div class="main-header">', unsafe_allow_html=True)
    st.markdown('<div class="flag-stripe"></div>', unsafe_allow_html=True)
    st.title("⚖ Kanoon ki Pehchaan")
    st.markdown('</div>', unsafe_allow_html=True)

    d = c = q = ph = sm = p_url = ""
    try:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE name = %s", (username,))
            users = cursor.fetchall()
            cursor.close()
            conn.close()
            if users:
                user = users[0]
                d = user.get('degree', '') or ""
                c = user.get('college', '') or ""
                q = user.get('myQualifications', '') or ""
                ph = user.get('Phone_No', '') or ""
                sm = user.get('social_media', '') or ""
                p_url = user.get('profile_pic_url', '') or ""
            else:
                st.info("No profile data found. Let's create your profile!")
    except Exception as e:
        logger.error(f"Error fetching user data: {e}")
        st.error("Error retrieving your profile data.")

    st.markdown('<div class="card animate-fadeIn">', unsafe_allow_html=True)
    st.subheader("Edit Your Profile")
    new_degree = st.text_input("Degree", value=d, placeholder="Your educational degree")
    new_college = st.text_input("College/University", value=c, placeholder="Your educational institution")
    new_qualifications = st.text_area("Qualifications", value=q, placeholder="Your professional qualifications")
    new_phone_no = st.text_input("Phone Number", value=ph, placeholder="Your contact number")
    new_sm = st.text_input("Social Media", value=sm, placeholder="Your social media links")
    new_profile_pic = st.file_uploader("Update Profile Picture", type=["jpg", "png", "jpeg"])
    if st.button("Update Profile"):
        try:
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()
                update_fields = []
                update_values = []
                if new_degree:
                    update_fields.append("degree = %s")
                    update_values.append(new_degree)
                if new_college:
                    update_fields.append("college = %s")
                    update_values.append(new_college)
                if new_qualifications:
                    update_fields.append("myQualifications = %s")
                    update_values.append(new_qualifications)
                if new_phone_no:
                    update_fields.append("Phone_No = %s")
                    update_values.append(new_phone_no)
                if new_sm:
                    update_fields.append("social_media = %s")
                    update_values.append(new_sm)
                if new_profile_pic:
                    image_dir = "images"
                    os.makedirs(image_dir, exist_ok=True)
                    image_path = os.path.join(image_dir, f"{username}.jpg")
                    with open(image_path, "wb") as f:
                        f.write(new_profile_pic.read())
                    update_fields.append("profile_pic_url = %s")
                    update_values.append(image_path)
                if update_fields:
                    update_query = f"UPDATE users SET {', '.join(update_fields)} WHERE name = %s"
                    update_values.append(username)
                    cursor.execute(update_query, update_values)
                    conn.commit()
                    st.success("Profile updated successfully!")
                else:
                    st.info("No changes to update.")
                cursor.close()
                conn.close()
        except Exception as e:
            logger.error(f"Error updating profile: {e}")
            st.error(f"Error updating profile: {str(e)}")
    st.page_link("pages/lawyer.py", label="Go back to Profile", icon="🔙")
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="footer">Edit your lawyer profile</div>', unsafe_allow_html=True)