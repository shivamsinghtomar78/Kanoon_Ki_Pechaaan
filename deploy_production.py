#!/usr/bin/env python3
"""
Production Deployment Script for Kanoon Ki Pechaan
Handles production setup and deployment with Gunicorn
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

def check_requirements():
    """Check if all production requirements are met"""
    print("🔍 Checking production requirements...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        return False
    
    # Check if .env file exists
    if not Path('.env').exists():
        print("❌ .env file not found. Please create one from .env.template")
        return False
    
    # Check if required directories exist
    required_dirs = ['backend', 'frontend', 'uploads']
    for dir_name in required_dirs:
        if not Path(dir_name).exists():
            print(f"❌ Required directory '{dir_name}' not found")
            return False
    
    print("✅ All production requirements met")
    return True

def install_dependencies():
    """Install production dependencies"""
    print("📦 Installing production dependencies...")
    
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True, capture_output=True)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def setup_database():
    """Initialize database for production"""
    print("🗄️ Setting up database...")
    
    try:
        # Import and run database setup
        from setup_database import main as setup_db
        setup_db()
        print("✅ Database setup completed")
        return True
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        return False

def create_gunicorn_config():
    """Create Gunicorn configuration file"""
    gunicorn_config = '''# Gunicorn configuration file for production
import multiprocessing
import os

# Server socket
bind = f"{os.getenv('APP_HOST', '0.0.0.0')}:{os.getenv('FLASK_PORT', '5000')}"
backlog = 2048

# Worker processes
workers = int(os.getenv('GUNICORN_WORKERS', multiprocessing.cpu_count() * 2 + 1))
worker_class = "sync"
worker_connections = 1000
timeout = int(os.getenv('GUNICORN_TIMEOUT', 120))
keepalive = 5

# Restart workers after this many requests, to help prevent memory leaks
max_requests = 1000
max_requests_jitter = 50

# Logging
accesslog = "logs/gunicorn_access.log"
errorlog = "logs/gunicorn_error.log"
loglevel = os.getenv('LOG_LEVEL', 'info').lower()
capture_output = True

# Process naming
proc_name = 'kanoon_ki_pechaan'

# Server mechanics
daemon = False
pidfile = 'gunicorn.pid'
user = None
group = None
tmp_upload_dir = None

# SSL (uncomment and configure for HTTPS)
# keyfile = '/path/to/private.key'
# certfile = '/path/to/certificate.crt'

# Security
limit_request_line = 4096
limit_request_fields = 100
limit_request_field_size = 8190
'''
    
    with open('gunicorn.conf.py', 'w') as f:
        f.write(gunicorn_config)
    
    print("✅ Gunicorn configuration created")

def create_logs_directory():
    """Create logs directory for production"""
    logs_dir = Path('logs')
    logs_dir.mkdir(exist_ok=True)
    print("✅ Logs directory created")

def create_systemd_service():
    """Create systemd service file for production deployment"""
    current_dir = Path.cwd()
    venv_path = Path(sys.executable).parent.parent
    
    service_content = f'''[Unit]
Description=Kanoon Ki Pechaan Flask Application
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory={current_dir}
Environment=PATH={venv_path}/bin
EnvironmentFile={current_dir}/.env
ExecStart={venv_path}/bin/gunicorn --config gunicorn.conf.py app:create_app()
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
'''
    
    with open('kanoon-ki-pechaan.service', 'w') as f:
        f.write(service_content)
    
    print("✅ Systemd service file created: kanoon-ki-pechaan.service")
    print("   Copy this to /etc/systemd/system/ to enable automatic startup")

def create_nginx_config():
    """Create Nginx configuration for reverse proxy"""
    nginx_config = '''# Nginx configuration for Kanoon Ki Pechaan
server {
    listen 80;
    server_name your-domain.com;  # Replace with your domain
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
    
    # File upload size limit
    client_max_body_size 50M;
    
    # Static files
    location /static/ {
        alias /path/to/your/project/frontend/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Main application
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}

# HTTPS configuration (uncomment after obtaining SSL certificate)
# server {
#     listen 443 ssl http2;
#     server_name your-domain.com;
#     
#     ssl_certificate /path/to/your/certificate.crt;
#     ssl_certificate_key /path/to/your/private.key;
#     
#     # Include the location blocks from above
# }
'''
    
    with open('nginx.conf', 'w') as f:
        f.write(nginx_config)
    
    print("✅ Nginx configuration created: nginx.conf")

def main():
    """Main deployment function"""
    print("🚀 Starting production deployment for Kanoon Ki Pechaan...")
    print("=" * 60)
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Setup database
    if not setup_database():
        print("⚠️  Database setup failed, but continuing with deployment")
    
    # Create production files
    create_logs_directory()
    create_gunicorn_config()
    create_systemd_service()
    create_nginx_config()
    
    print("\n" + "=" * 60)
    print("✅ Production deployment setup completed!")
    print("\nNext steps:")
    print("1. Copy kanoon-ki-pechaan.service to /etc/systemd/system/")
    print("2. Configure nginx.conf for your domain")
    print("3. Set DEVELOPMENT_MODE=False in .env")
    print("4. Start the service: sudo systemctl start kanoon-ki-pechaan")
    print("5. Enable auto-start: sudo systemctl enable kanoon-ki-pechaan")
    print("\nTo start in development mode:")
    print("python run_flask.py")
    print("\nTo start with Gunicorn:")
    print("gunicorn --config gunicorn.conf.py app:create_app()")
    print("=" * 60)

if __name__ == '__main__':
    main()