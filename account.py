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

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="0819",
        database="lawyers"
    )

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
api_key = os.getenv("FIREBASE_API_KEY")

if not api_key:
    logger.error("Firebase API key not found.")
    st.error("Configuration error: Firebase API key not available.")

# Initialize Firebase
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

# Page configuration
st.set_page_config(
    page_title="Kanoon ki Pehchaan",
    page_icon="⚖",
    layout="centered",
    initial_sidebar_state="collapsed"
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

# Firebase Authentication functions
def sign_up_with_email_and_password(email, password, username=None):
    if not email or not password:
        st.error("Email and password are required.")
        return False
    if not username:
        username = email.split('@')[0]
    try:
        if not init_firebase():
            return False
        user = auth.create_user(email=email, password=password, display_name=username)
        logger.info(f"User created successfully: {email}")
        st.success('Account created successfully!')
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users VALUES(%s, NULL, NULL, NULL, NULL, NULL, NULL);", (username,))
        conn.commit()
        cursor.close()
        conn.close()
        st.session_state.username = username
        st.session_state.useremail = email
        st.session_state.authenticated = True
        st.switch_page("pages/home.py")
        return True
    except Exception as e:
        error_message = str(e)
        logger.error(f"Signup failed: {error_message}")
        if "EMAIL_EXISTS" in error_message:
            st.error("This email is already registered.")
        elif "WEAK_PASSWORD" in error_message:
            st.error("Password should be at least 6 characters long.")
        elif "INVALID_EMAIL" in error_message:
            st.error("Please enter a valid email address.")
        else:
            st.error(f"Signup failed: {error_message}")
        return False

def sign_in_with_email_and_password(email, password):
    if not email or not password:
        st.error("Email and password are required.")
        return False
    try:
        rest_api_url = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword"
        payload = {"email": email, "password": password, "returnSecureToken": True}
        r = requests.post(rest_api_url, params={"key": api_key}, data=json.dumps(payload))
        data = r.json()
        if 'email' in data:
            logger.info(f"User logged in successfully: {email}")
            st.session_state.username = data.get('displayName', 'User')
            st.session_state.useremail = data['email']
            st.session_state.authenticated = True
            st.switch_page("pages/home.py")
            return True
        else:
            error_code = data.get('error', {}).get('message', 'Unknown error')
            logger.error(f"Login failed: {error_code}")
            if "EMAIL_NOT_FOUND" in error_code:
                st.error("Email not found.")
            elif "INVALID_PASSWORD" in error_code:
                st.error("Invalid password.")
            elif "USER_DISABLED" in error_code:
                st.error("This account has been disabled.")
            else:
                st.error(f"Login failed: {error_code}")
            return False
    except Exception as e:
        logger.error(f"Signin failed: {e}")
        st.error("An error occurred during login.")
        return False

def reset_password(email):
    if not email:
        return False, "Email address is required."
    try:
        rest_api_url = "https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode"
        payload = {"email": email, "requestType": "PASSWORD_RESET"}
        r = requests.post(rest_api_url, params={"key": api_key}, data=json.dumps(payload))
        if r.status_code == 200:
            logger.info(f"Password reset email sent to: {email}")
            return True, "Password reset email sent successfully."
        else:
            error_message = r.json().get('error', {}).get('message', 'Unknown error')
            logger.error(f"Password reset failed: {error_message}")
            if "EMAIL_NOT_FOUND" in error_message:
                return False, "Email not found."
            else:
                return False, f"Password reset failed: {error_message}"
    except Exception as e:
        logger.error(f"Password reset exception: {e}")
        return False, f"An error occurred: {str(e)}"

def forget():
    st.subheader("Reset Password")
    email = st.text_input('Email Address', key='reset_email')
    if st.button('Send Reset Link'):
        if not email:
            st.warning("Please enter your email address.")
        else:
            success, message = reset_password(email)
            if success:
                st.success(message)
            else:
                st.warning(message)

def auth_page():
    st.markdown('<div class="main-header">', unsafe_allow_html=True)
    st.markdown('<div class="flag-stripe"></div>', unsafe_allow_html=True)
    st.title("⚖ Kanoon ki Pehchaan")
    st.caption("Your AI-powered Guide to Indian Legal System")
    st.markdown('</div>', unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["Login", "Sign Up", "Forgot Password"])
    with tab1:
        st.markdown('<div class="card animate-fadeIn">', unsafe_allow_html=True)
        st.subheader("Login to Your Account")
        email = st.text_input('Email Address', key='login_email')
        password = st.text_input('Password', type='password', key='login_password')
        if st.button('Login', key='login_button'):
            sign_in_with_email_and_password(email, password)
        st.markdown('</div>', unsafe_allow_html=True)
    with tab2:
        st.markdown('<div class="card animate-fadeIn">', unsafe_allow_html=True)
        st.subheader("Create New Account")
        username = st.text_input('Username (Optional)', key='signup_username')
        email = st.text_input('Email Address', key='signup_email')
        password = st.text_input('Password', type='password', key='signup_password')
        confirm_password = st.text_input('Confirm Password', type='password', key='signup_confirm_password')
        terms_agree = st.checkbox('I agree to the Terms and Conditions')
        if st.button('Sign Up', key='signup_button'):
            if password != confirm_password:
                st.error('Passwords do not match.')
            elif not terms_agree:
                st.error('You must agree to the Terms and Conditions.')
            else:
                sign_up_with_email_and_password(email, password, username)
        st.markdown('</div>', unsafe_allow_html=True)
    with tab3:
        st.markdown('<div class="card animate-fadeIn">', unsafe_allow_html=True)
        forget()
        st.markdown('</div>', unsafe_allow_html=True)

def main():
    if st.session_state.get('authenticated', False):
        st.switch_page("pages/home.py")
    else:
        auth_page()
    st.markdown('<div class="footer">Powered by Firebase</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()