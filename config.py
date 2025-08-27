"""
Configuration module for Kanoon Ki Pechaan
Handles environment variables and application settings securely
"""
import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from typing import Optional

# Load environment variables
load_dotenv()

class Config:
    """Application configuration class"""
    
    # Firebase Configuration
    FIREBASE_API_KEY: str = os.getenv("FIREBASE_API_KEY", "")
    FIREBASE_PROJECT_ID: str = os.getenv("FIREBASE_PROJECT_ID", "")
    FIREBASE_STORAGE_BUCKET: str = os.getenv("FIREBASE_STORAGE_BUCKET", "")
    FIREBASE_CREDENTIALS_FILE: str = "kanoon-ki-pehchaan-6ff0ed4a9c13.json"
    
    # Google AI Configuration
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    
    # Database Configuration
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_USER: str = os.getenv("DB_USER", "root")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")
    DB_NAME: str = os.getenv("DB_NAME", "lawyers")
    DB_PORT: int = int(os.getenv("DB_PORT", "3306"))
    
    # Security Configuration
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "jwt-secret-key-change-in-production")
    
    # Indian Kanoon API Configuration
    INDIAN_KANOON_API_KEY: str = os.getenv("INDIAN_KANOON_API_KEY", "")
    INDIAN_KANOON_BASE_URL: str = os.getenv("INDIAN_KANOON_BASE_URL", "https://api.indiankanoon.org")
    
    # Application Configuration
    APP_DEBUG: bool = os.getenv("APP_DEBUG", "False").lower() == "true"
    APP_HOST: str = os.getenv("APP_HOST", "localhost")
    APP_PORT: int = int(os.getenv("APP_PORT", "8501"))
    FLASK_PORT: int = int(os.getenv("FLASK_PORT", "5000"))
    DEVELOPMENT_MODE: bool = os.getenv("DEVELOPMENT_MODE", "False").lower() == "true"
    
    # SQLAlchemy Configuration (after DEVELOPMENT_MODE is defined)
    # Use SQLite as fallback if MySQL is not available in development
    USE_SQLITE = os.getenv("USE_SQLITE", "false").lower() == "true"
    
    if USE_SQLITE or (DEVELOPMENT_MODE and os.getenv("FORCE_SQLITE")):
        SQLALCHEMY_DATABASE_URI: str = "sqlite:///kanoon_ki_pechaan.db"
        print("Using SQLite database")
    else:
        SQLALCHEMY_DATABASE_URI: str = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
    
    # File Upload Configuration
    MAX_FILE_SIZE_MB: int = int(os.getenv("MAX_FILE_SIZE_MB", "50"))
    UPLOAD_FOLDER: str = os.getenv("UPLOAD_FOLDER", "uploads")
    ALLOWED_EXTENSIONS: set = set(os.getenv("ALLOWED_EXTENSIONS", "pdf,doc,docx,txt").split(","))
    
    # Email Configuration
    SMTP_SERVER: str = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    EMAIL_USERNAME: str = os.getenv("EMAIL_USERNAME", "")
    EMAIL_PASSWORD: str = os.getenv("EMAIL_PASSWORD", "")
    
    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "app.log")
    
    # Production Configuration
    MAX_CONTENT_LENGTH: int = MAX_FILE_SIZE_MB * 1024 * 1024  # Convert to bytes
    SESSION_COOKIE_SECURE: bool = not DEVELOPMENT_MODE
    SESSION_COOKIE_HTTPONLY: bool = True
    SESSION_COOKIE_SAMESITE: str = 'Lax'
    PERMANENT_SESSION_LIFETIME: int = 3600  # 1 hour
    
    # CORS Configuration
    CORS_ORIGINS: list = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")
    
    # Rate Limiting
    RATELIMIT_STORAGE_URL: str = os.getenv("REDIS_URL", "memory://")
    
    # Gunicorn Configuration (for production)
    GUNICORN_WORKERS: int = int(os.getenv("GUNICORN_WORKERS", "4"))
    GUNICORN_TIMEOUT: int = int(os.getenv("GUNICORN_TIMEOUT", "120"))
    
    @classmethod
    def validate_config(cls) -> bool:
        """Validate essential configuration values"""
        errors = []
        
        # Skip Firebase validation in development mode
        if not cls.DEVELOPMENT_MODE:
            if not cls.FIREBASE_API_KEY:
                errors.append("FIREBASE_API_KEY is required")
            
            if not Path(cls.FIREBASE_CREDENTIALS_FILE).exists():
                errors.append(f"Firebase credentials file {cls.FIREBASE_CREDENTIALS_FILE} not found")
        else:
            logger.info("Running in development mode - skipping Firebase validation")
        
        if not cls.GOOGLE_API_KEY:
            errors.append("GOOGLE_API_KEY is required")
        
        if not cls.DB_PASSWORD:
            errors.append("DB_PASSWORD is required")
        
        if errors:
            logging.error("Configuration validation failed:")
            for error in errors:
                logging.error(f"  - {error}")
            return False
        
        return True
    
    @classmethod
    def get_db_config(cls) -> dict:
        """Get database configuration as dictionary"""
        return {
            "host": cls.DB_HOST,
            "user": cls.DB_USER,
            "password": cls.DB_PASSWORD,
            "database": cls.DB_NAME,
            "port": cls.DB_PORT
        }
    
    @classmethod
    def setup_logging(cls):
        """Setup application logging"""
        logging.basicConfig(
            level=getattr(logging, cls.LOG_LEVEL.upper()),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(cls.LOG_FILE),
                logging.StreamHandler()
            ]
        )

# Create uploads directory if it doesn't exist
upload_path = Path(Config.UPLOAD_FOLDER)
upload_path.mkdir(exist_ok=True)

# Setup logging
Config.setup_logging()

# Get logger for this module
logger = logging.getLogger(__name__)

def get_config() -> Config:
    """Get application configuration instance"""
    return Config

def validate_environment() -> bool:
    """Validate environment configuration on startup"""
    if not Config.validate_config():
        logger.error("Environment validation failed. Please check your .env file.")
        return False
    
    logger.info("Environment configuration validated successfully")
    return True