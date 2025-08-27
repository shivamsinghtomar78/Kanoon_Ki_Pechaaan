#!/usr/bin/env python3
"""
Simple Flask Application Startup Script for Development
Uses SQLite database to avoid MySQL dependency issues
"""

import os
import sys
from pathlib import Path

# Set SQLite mode for development
os.environ['USE_SQLITE'] = 'true'
os.environ['DEVELOPMENT_MODE'] = 'true'

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

def main():
    """Main function to start the Flask application"""
    print("🚀 Starting Kanoon Ki Pechaan Flask Application (Development Mode)")
    print("=" * 60)
    print("Using SQLite database for development...")
    
    try:
        # Create Flask app
        app = create_app()
        
        # Create database tables
        with app.app_context():
            from backend.models import db
            db.create_all()
            print("✅ SQLite database tables created successfully")
        
        print("✅ Flask application created successfully")
        
        # Print application info
        print("\n📋 Application Information:")
        print(f"   • Host: {Config.APP_HOST}")
        print(f"   • Port: {Config.FLASK_PORT}")
        print(f"   • Debug Mode: {Config.APP_DEBUG}")
        print(f"   • Database: SQLite (Development)")
        
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
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()