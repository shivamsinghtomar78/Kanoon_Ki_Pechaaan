"""
Database initialization script for Kanoon Ki Pechaan
Creates database, tables, and initial data
"""
import mysql.connector
from mysql.connector import Error
import logging
from config import Config
import sys
import getpass

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DatabaseSetup:
    """Database setup and initialization class"""
    
    def __init__(self):
        self.config = Config.get_db_config()
        self.connection = None
        
    def create_connection(self, include_database=True):
        """Create database connection"""
        try:
            config = self.config.copy()
            if not include_database:
                config.pop('database', None)
            
            self.connection = mysql.connector.connect(**config)
            if self.connection.is_connected():
                logger.info(f"Connected to MySQL server {'with database' if include_database else 'without database'}")
                return True
        except Error as e:
            logger.error(f"Error connecting to MySQL: {e}")
            return False
        
        return False
    
    def close_connection(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            logger.info("MySQL connection closed")
    
    def create_database(self):
        """Create the database if it doesn't exist"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.config['database']}")
            cursor.execute(f"USE {self.config['database']}")
            logger.info(f"Database '{self.config['database']}' created/selected successfully")
            cursor.close()
            return True
        except Error as e:
            logger.error(f"Error creating database: {e}")
            return False
    
    def create_users_table(self):
        """Create users table for lawyer profiles"""
        try:
            cursor = self.connection.cursor()
            
            create_users_table_query = """
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL UNIQUE,
                email VARCHAR(255) UNIQUE,
                degree VARCHAR(255),
                college VARCHAR(255),
                myQualifications TEXT,
                Phone_No VARCHAR(20),
                social_media TEXT,
                profile_pic_url VARCHAR(500),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE,
                INDEX idx_name (name),
                INDEX idx_email (email)
            )
            """
            
            cursor.execute(create_users_table_query)
            logger.info("Users table created successfully")
            cursor.close()
            return True
        except Error as e:
            logger.error(f"Error creating users table: {e}")
            return False
    
    def create_legal_queries_table(self):
        """Create table to store legal queries and responses"""
        try:
            cursor = self.connection.cursor()
            
            create_queries_table_query = """
            CREATE TABLE IF NOT EXISTS legal_queries (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_email VARCHAR(255),
                query_text TEXT NOT NULL,
                response_text TEXT,
                query_type VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                response_time_ms INT,
                satisfaction_rating INT CHECK (satisfaction_rating >= 1 AND satisfaction_rating <= 5),
                INDEX idx_user_email (user_email),
                INDEX idx_created_at (created_at),
                INDEX idx_query_type (query_type)
            )
            """
            
            cursor.execute(create_queries_table_query)
            logger.info("Legal queries table created successfully")
            cursor.close()
            return True
        except Error as e:
            logger.error(f"Error creating legal queries table: {e}")
            return False
    
    def create_documents_table(self):
        """Create table to store document analysis records"""
        try:
            cursor = self.connection.cursor()
            
            create_documents_table_query = """
            CREATE TABLE IF NOT EXISTS documents (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_email VARCHAR(255),
                filename VARCHAR(255) NOT NULL,
                file_path VARCHAR(500),
                file_size_bytes INT,
                document_type VARCHAR(50),
                summary TEXT,
                key_points JSON,
                analysis_status ENUM('pending', 'processing', 'completed', 'failed') DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                processed_at TIMESTAMP NULL,
                INDEX idx_user_email (user_email),
                INDEX idx_status (analysis_status),
                INDEX idx_created_at (created_at)
            )
            """
            
            cursor.execute(create_documents_table_query)
            logger.info("Documents table created successfully")
            cursor.close()
            return True
        except Error as e:
            logger.error(f"Error creating documents table: {e}")
            return False
    
    def create_lawyer_client_connections_table(self):
        """Create table to track lawyer-client connections"""
        try:
            cursor = self.connection.cursor()
            
            create_connections_table_query = """
            CREATE TABLE IF NOT EXISTS lawyer_client_connections (
                id INT AUTO_INCREMENT PRIMARY KEY,
                client_email VARCHAR(255) NOT NULL,
                lawyer_name VARCHAR(255) NOT NULL,
                case_details TEXT,
                connection_status ENUM('requested', 'accepted', 'declined', 'completed') DEFAULT 'requested',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                notes TEXT,
                INDEX idx_client_email (client_email),
                INDEX idx_lawyer_name (lawyer_name),
                INDEX idx_status (connection_status),
                FOREIGN KEY (lawyer_name) REFERENCES users(name) ON DELETE CASCADE
            )
            """
            
            cursor.execute(create_connections_table_query)
            logger.info("Lawyer-client connections table created successfully")
            cursor.close()
            return True
        except Error as e:
            logger.error(f"Error creating lawyer-client connections table: {e}")
            return False
    
    def insert_sample_data(self):
        """Insert sample lawyer data"""
        try:
            cursor = self.connection.cursor()
            
            sample_lawyers = [
                (
                    "Dr. Rajesh Kumar",
                    "rajesh.kumar@legalfirm.com",
                    "LLB, LLM",
                    "Delhi University Law Faculty",
                    "15+ years in Constitutional Law, Supreme Court practice",
                    "+91-9876543210",
                    "LinkedIn: rajesh-kumar-lawyer",
                    "uploads/profiles/default_lawyer.jpg"
                ),
                (
                    "Advocate Priya Sharma",
                    "priya.sharma@lawchambers.com",
                    "BA LLB (Hons)",
                    "National Law University, Delhi",
                    "Criminal Law specialist, High Court advocate",
                    "+91-9876543211",
                    "Twitter: @PriyaSharmaLaw",
                    "uploads/profiles/default_lawyer.jpg"
                ),
                (
                    "Shri Vikram Singh",
                    "vikram.singh@legal.com",
                    "LLB, Diploma in Taxation",
                    "Mumbai University",
                    "Corporate Law, Taxation, Contract disputes",
                    "+91-9876543212",
                    "LinkedIn: vikram-singh-advocate",
                    "uploads/profiles/default_lawyer.jpg"
                )
            ]
            
            insert_query = """
            INSERT IGNORE INTO users (name, email, degree, college, myQualifications, Phone_No, social_media, profile_pic_url)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            cursor.executemany(insert_query, sample_lawyers)
            self.connection.commit()
            
            logger.info(f"Inserted {cursor.rowcount} sample lawyer profiles")
            cursor.close()
            return True
        except Error as e:
            logger.error(f"Error inserting sample data: {e}")
            return False
    
    def setup_database(self):
        """Complete database setup process"""
        logger.info("Starting database setup...")
        
        # Connect without database first
        if not self.create_connection(include_database=False):
            return False
        
        # Create database
        if not self.create_database():
            self.close_connection()
            return False
        
        # Reconnect with database
        self.close_connection()
        if not self.create_connection(include_database=True):
            return False
        
        # Create tables
        tables_created = (
            self.create_users_table() and
            self.create_legal_queries_table() and
            self.create_documents_table() and
            self.create_lawyer_client_connections_table()
        )
        
        if not tables_created:
            self.close_connection()
            return False
        
        # Insert sample data
        if not self.insert_sample_data():
            logger.warning("Failed to insert sample data, but database setup completed")
        
        self.close_connection()
        logger.info("Database setup completed successfully!")
        return True

def interactive_setup():
    """Interactive database setup with user input"""
    print("🏛️ Kanoon Ki Pechaan - Database Setup")
    print("=" * 50)
    
    # Check if .env file exists
    if not Config.DB_PASSWORD:
        print("⚠️  Database password not found in environment variables.")
        password = getpass.getpass("Please enter MySQL root password: ")
        Config.DB_PASSWORD = password
    
    print(f"Setting up database: {Config.DB_NAME}")
    print(f"Host: {Config.DB_HOST}:{Config.DB_PORT}")
    print(f"User: {Config.DB_USER}")
    
    confirm = input("\nProceed with database setup? (y/N): ")
    if confirm.lower() != 'y':
        print("Database setup cancelled.")
        return False
    
    setup = DatabaseSetup()
    return setup.setup_database()

def main():
    """Main function for database setup"""
    try:
        if interactive_setup():
            print("✅ Database setup completed successfully!")
            print("\n🚀 You can now run the application with: streamlit run account.py")
        else:
            print("❌ Database setup failed!")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup interrupted by user.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error during setup: {e}")
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()