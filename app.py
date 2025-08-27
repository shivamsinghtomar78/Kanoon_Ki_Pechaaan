"""
Flask Application Entry Point
Kanoon Ki Pechaan - Legal AI Platform
"""
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
from flask_login import LoginManager
import os
import logging
from datetime import timedelta

# Import configurations and models
from config import Config
from backend.models import db, User
from backend.auth import auth_bp
from backend.chatbot import chatbot_bp
from backend.documents import documents_bp
from backend.lawyers import lawyers_bp

def create_app():
    """Application factory pattern"""
    app = Flask(__name__, 
                template_folder='frontend/templates',
                static_folder='frontend/static')
    
    # Load configuration
    app.config.from_object(Config)
    app.config['SECRET_KEY'] = Config.SECRET_KEY
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=2)
    
    # Enable CORS for frontend-backend communication
    CORS(app, origins=['http://localhost:3000', 'http://127.0.0.1:3000'])
    
    # Initialize extensions
    db.init_app(app)
    
    # Login Manager setup
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(chatbot_bp, url_prefix='/api/chatbot')
    app.register_blueprint(documents_bp, url_prefix='/api/documents')
    app.register_blueprint(lawyers_bp, url_prefix='/api/lawyers')
    
    # Frontend routes
    @app.route('/')
    def index():
        """Main landing page"""
        return render_template('index.html')
    
    @app.route('/login')
    def login_page():
        """Login page"""
        return render_template('auth/login.html')
    
    @app.route('/register')
    def register_page():
        """Registration page"""
        return render_template('auth/register.html')
    
    @app.route('/dashboard')
    def dashboard():
        """User dashboard"""
        if 'user_id' not in session:
            return redirect(url_for('login_page'))
        return render_template('dashboard/home.html')
    
    @app.route('/features/chatbot')
    def chatbot_page():
        """AI Chatbot page"""
        if 'user_id' not in session:
            return redirect(url_for('login_page'))
        return render_template('features/chatbot.html')
    
    @app.route('/features/documents')
    def documents_page():
        """Document analyzer page"""
        if 'user_id' not in session:
            return redirect(url_for('login_page'))
        return render_template('features/documents.html')
    
    @app.route('/features/lawyers')
    def lawyers_page():
        """Lawyer network page"""
        if 'user_id' not in session:
            return redirect(url_for('login_page'))
        return render_template('features/lawyers.html')
    
    @app.route('/profile')
    def profile_page():
        """User profile page"""
        if 'user_id' not in session:
            return redirect(url_for('login_page'))
        return render_template('profile.html')
    
    # Health check endpoint
    @app.route('/api/health')
    def health_check():
        """Health check endpoint"""
        return jsonify({
            'status': 'healthy',
            'message': 'Kanoon Ki Pechaan API is running',
            'version': '2.0.0'
        })
    
    # Error handlers
    @app.errorhandler(404)
    def page_not_found(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return render_template('errors/500.html'), 500
    
    # Setup logging
    if not app.debug:
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s %(levelname)s: %(message)s',
            handlers=[
                logging.FileHandler('app.log'),
                logging.StreamHandler()
            ]
        )
    
    return app

if __name__ == '__main__':
    app = create_app()
    
    # Create database tables
    with app.app_context():
        db.create_all()
        print("✅ Database tables created successfully")
    
    # Run application
    print("🚀 Starting Kanoon Ki Pechaan Flask Application...")
    app.run(
        host=Config.APP_HOST,
        port=Config.FLASK_PORT,
        debug=Config.APP_DEBUG
    )