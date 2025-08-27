"""
Authentication API Blueprint
Handles user registration, login, logout, and profile management
"""
from flask import Blueprint, request, jsonify, session
from flask_login import login_user, logout_user, login_required, current_user
from backend.models import db, User
from config import Config
import logging
import jwt
from datetime import datetime, timedelta
import re

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__)

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Validate password strength"""
    if len(password) < 6:
        return False, "Password must be at least 6 characters long"
    return True, "Password is valid"

def generate_jwt_token(user_id):
    """Generate JWT token for user"""
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, Config.JWT_SECRET_KEY, algorithm='HS256')

@auth_bp.route('/register', methods=['POST'])
def register():
    """User registration endpoint"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'email', 'password']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'message': f'{field.capitalize()} is required'
                }), 400
        
        name = data['name'].strip()
        email = data['email'].strip().lower()
        password = data['password']
        user_type = data.get('user_type', 'user')
        
        # Validate email format
        if not validate_email(email):
            return jsonify({
                'success': False,
                'message': 'Invalid email format'
            }), 400
        
        # Validate password
        is_valid, message = validate_password(password)
        if not is_valid:
            return jsonify({
                'success': False,
                'message': message
            }), 400
        
        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({
                'success': False,
                'message': 'Email already registered'
            }), 409
        
        # Create new user
        new_user = User(
            name=name,
            email=email,
            user_type=user_type,
            phone_no=data.get('phone_no'),
            degree=data.get('degree') if user_type == 'lawyer' else None,
            college=data.get('college') if user_type == 'lawyer' else None,
            qualifications=data.get('qualifications') if user_type == 'lawyer' else None
        )
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        # Generate JWT token
        token = generate_jwt_token(new_user.id)
        
        # Set session
        session['user_id'] = new_user.id
        session['user_email'] = new_user.email
        session['user_type'] = new_user.user_type
        session.permanent = True
        
        logger.info(f"New user registered: {email}")
        
        return jsonify({
            'success': True,
            'message': 'Registration successful',
            'user': new_user.to_dict(),
            'token': token
        }), 201
        
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Registration failed. Please try again.'
        }), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """User login endpoint"""
    try:
        data = request.get_json()
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({
                'success': False,
                'message': 'Email and password are required'
            }), 400
        
        # Find user by email
        user = User.query.filter_by(email=email).first()
        
        if not user or not user.check_password(password):
            return jsonify({
                'success': False,
                'message': 'Invalid email or password'
            }), 401
        
        if not user.is_active:
            return jsonify({
                'success': False,
                'message': 'Account is deactivated'
            }), 401
        
        # Generate JWT token
        token = generate_jwt_token(user.id)
        
        # Set session
        session['user_id'] = user.id
        session['user_email'] = user.email
        session['user_type'] = user.user_type
        session.permanent = True
        
        # Login user with Flask-Login
        login_user(user)
        
        logger.info(f"User logged in: {email}")
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'user': user.to_dict(),
            'token': token
        }), 200
        
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Login failed. Please try again.'
        }), 500

@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    """User logout endpoint"""
    try:
        # Clear session
        session.clear()
        
        # Logout user with Flask-Login
        logout_user()
        
        return jsonify({
            'success': True,
            'message': 'Logout successful'
        }), 200
        
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Logout failed'
        }), 500

@auth_bp.route('/profile', methods=['GET'])
@login_required
def get_profile():
    """Get current user profile"""
    try:
        return jsonify({
            'success': True,
            'user': current_user.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Get profile error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to fetch profile'
        }), 500

@auth_bp.route('/profile', methods=['PUT'])
@login_required
def update_profile():
    """Update user profile"""
    try:
        data = request.get_json()
        
        # Update allowed fields
        if 'name' in data:
            current_user.name = data['name'].strip()
        if 'phone_no' in data:
            current_user.phone_no = data['phone_no']
        if 'degree' in data and current_user.user_type == 'lawyer':
            current_user.degree = data['degree']
        if 'college' in data and current_user.user_type == 'lawyer':
            current_user.college = data['college']
        if 'qualifications' in data and current_user.user_type == 'lawyer':
            current_user.qualifications = data['qualifications']
        if 'social_media' in data:
            current_user.social_media = data['social_media']
        
        current_user.updated_at = datetime.utcnow()
        db.session.commit()
        
        logger.info(f"Profile updated for user: {current_user.email}")
        
        return jsonify({
            'success': True,
            'message': 'Profile updated successfully',
            'user': current_user.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Update profile error: {str(e)}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Failed to update profile'
        }), 500

@auth_bp.route('/change-password', methods=['PUT'])
@login_required
def change_password():
    """Change user password"""
    try:
        data = request.get_json()
        
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        
        if not current_password or not new_password:
            return jsonify({
                'success': False,
                'message': 'Current and new passwords are required'
            }), 400
        
        # Verify current password
        if not current_user.check_password(current_password):
            return jsonify({
                'success': False,
                'message': 'Current password is incorrect'
            }), 401
        
        # Validate new password
        is_valid, message = validate_password(new_password)
        if not is_valid:
            return jsonify({
                'success': False,
                'message': message
            }), 400
        
        # Update password
        current_user.set_password(new_password)
        current_user.updated_at = datetime.utcnow()
        db.session.commit()
        
        logger.info(f"Password changed for user: {current_user.email}")
        
        return jsonify({
            'success': True,
            'message': 'Password changed successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Change password error: {str(e)}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Failed to change password'
        }), 500

@auth_bp.route('/verify', methods=['GET'])
def verify_session():
    """Verify if user session is valid"""
    try:
        if 'user_id' in session:
            user = User.query.get(session['user_id'])
            if user and user.is_active:
                return jsonify({
                    'success': True,
                    'authenticated': True,
                    'user': user.to_dict()
                }), 200
        
        return jsonify({
            'success': True,
            'authenticated': False
        }), 200
        
    except Exception as e:
        logger.error(f"Session verification error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Session verification failed'
        }), 500