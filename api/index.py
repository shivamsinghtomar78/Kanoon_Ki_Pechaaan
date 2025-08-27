"""
Vercel entry point for Kanoon Ki Pechaan Flask Application
"""
import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import the Flask app
from app import create_app

# Create the app
application = create_app()

# Vercel requires the handler to be named "application"
# This is the entry point for Vercel
app = application

if __name__ == "__main__":
    # This is for local development
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))