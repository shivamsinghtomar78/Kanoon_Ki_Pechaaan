#!/usr/bin/env python3
"""
Kanoon Ki Pechaan - Flask Application Startup Script
Run this script to start the Flask backend server
"""

import os
import sys
import logging
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from app import create_app
    from config import Config
    print("✅ Successfully imported Flask application")
except ImportError as e:
    print(f"❌ Failed to import Flask application: {e}")
    print("Make sure you have installed all requirements: pip install -r requirements.txt")
    sys.exit(1)

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('flask_app.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )

def check_environment():
    """Check if required environment variables are set"""
    required_vars = [
        'SECRET_KEY',
        'JWT_SECRET_KEY',
        'GOOGLE_API_KEY',
        'DB_HOST',
        'DB_USER',
        'DB_PASSWORD',
        'DB_NAME'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("Please check your .env file or set these environment variables")
        return False
    
    print("✅ All required environment variables are set")
    return True

def check_database_connection():
    """Check database connection"""
    try:
        from backend.models import db
        app = create_app()
        
        with app.app_context():
            # Try to create tables (this will test the connection)
            db.create_all()
            
            # Check if we're using SQLite fallback
            if 'sqlite' in app.config['SQLALCHEMY_DATABASE_URI']:
                print("⚠️  Using SQLite fallback database (MySQL not available)")
                print("✅ SQLite database connection successful and tables created")
            else:
                print("✅ MySQL database connection successful and tables created")
            return True
    except Exception as e:
        if Config.DEVELOPMENT_MODE:
            print(f"⚠️  Database connection failed, trying SQLite fallback: {e}")
            try:
                # Force SQLite configuration by setting environment variable
                os.environ['USE_SQLITE'] = 'true'
                # Re-import config to pick up the change
                import importlib
                import config
                importlib.reload(config)
                from config import Config as ReloadedConfig
                
                app = create_app()
                with app.app_context():
                    db.create_all()
                    print("✅ SQLite fallback database connection successful and tables created")
                    return True
            except Exception as sqlite_error:
                print(f"❌ SQLite fallback also failed: {sqlite_error}")
                return False
        else:
            print(f"❌ Database connection failed: {e}")
            print("Please check your database configuration in .env file")
            return False

def main():
    """Main function to start the Flask application"""
    print("🚀 Starting Kanoon Ki Pechaan Flask Application...")
    print("=" * 60)
    
    # Setup logging
    setup_logging()
    
    # Check environment variables
    if not check_environment():
        sys.exit(1)
    
    # Check database connection
    if not check_database_connection():
        sys.exit(1)
    
    # Create Flask app
    try:
        app = create_app()
        print("✅ Flask application created successfully")
    except Exception as e:
        print(f"❌ Failed to create Flask application: {e}")
        sys.exit(1)
    
    # Print application info
    print("\n📋 Application Information:")
    print(f"   • Host: {Config.APP_HOST}")
    print(f"   • Port: {Config.FLASK_PORT}")
    print(f"   • Debug Mode: {Config.APP_DEBUG}")
    print(f"   • Environment: {'Development' if Config.DEVELOPMENT_MODE else 'Production'}")
    
    print("\n🔗 Available Routes:")
    print("   • Landing Page: http://localhost:5000/")
    print("   • Login: http://localhost:5000/login")
    print("   • Register: http://localhost:5000/register")
    print("   • Dashboard: http://localhost:5000/dashboard")
    print("   • Chatbot: http://localhost:5000/features/chatbot")
    print("   • Documents: http://localhost:5000/features/documents")
    print("   • Lawyers: http://localhost:5000/features/lawyers")
    print("   • Profile: http://localhost:5000/profile")
    print("   • API Health: http://localhost:5000/api/health")
    
    print("\n" + "=" * 60)
    print("🎯 Application is starting...")
    print("Press Ctrl+C to stop the server")
    print("=" * 60)
    
    try:
        # Run the Flask application
        app.run(
            host=Config.APP_HOST,
            port=Config.FLASK_PORT,
            debug=Config.APP_DEBUG,
            threaded=True
        )
    except KeyboardInterrupt:
        print("\n\n👋 Application stopped by user")
    except Exception as e:
        print(f"\n❌ Application crashed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()