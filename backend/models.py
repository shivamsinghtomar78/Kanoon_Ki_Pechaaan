"""
Database Models for Kanoon Ki Pechaan
SQLAlchemy models for user management, documents, and lawyer profiles
"""
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import json

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """User model for authentication and profile management"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=True)
    phone_no = db.Column(db.String(20), nullable=True)
    user_type = db.Column(db.String(20), default='user')  # 'user' or 'lawyer'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Lawyer-specific fields
    degree = db.Column(db.String(200), nullable=True)
    college = db.Column(db.String(200), nullable=True)
    qualifications = db.Column(db.Text, nullable=True)
    social_media = db.Column(db.String(200), nullable=True)
    profile_pic_url = db.Column(db.String(500), nullable=True)
    
    # Relationships
    documents = db.relationship('Document', backref='user', lazy=True)
    chat_sessions = db.relationship('ChatSession', backref='user', lazy=True)
    
    def set_password(self, password):
        """Set password hash"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password against hash"""
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convert user to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone_no': self.phone_no,
            'user_type': self.user_type,
            'degree': self.degree,
            'college': self.college,
            'qualifications': self.qualifications,
            'social_media': self.social_media,
            'profile_pic_url': self.profile_pic_url,
            'created_at': self.created_at.isoformat(),
            'is_active': self.is_active
        }
    
    def __repr__(self):
        return f'<User {self.email}>'

class Document(db.Model):
    """Document model for file storage and analysis"""
    __tablename__ = 'documents'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    content_type = db.Column(db.String(100), nullable=False)
    
    # Analysis results
    extracted_text = db.Column(db.Text, nullable=True)
    summary = db.Column(db.Text, nullable=True)
    key_points = db.Column(db.Text, nullable=True)  # JSON string
    legal_analysis = db.Column(db.Text, nullable=True)
    
    # Metadata
    processed = db.Column(db.Boolean, default=False)
    processing_status = db.Column(db.String(50), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def set_key_points(self, points_list):
        """Set key points as JSON string"""
        self.key_points = json.dumps(points_list)
    
    def get_key_points(self):
        """Get key points as list"""
        if self.key_points:
            return json.loads(self.key_points)
        return []
    
    def to_dict(self):
        """Convert document to dictionary"""
        return {
            'id': self.id,
            'filename': self.filename,
            'original_filename': self.original_filename,
            'file_size': self.file_size,
            'content_type': self.content_type,
            'summary': self.summary,
            'key_points': self.get_key_points(),
            'legal_analysis': self.legal_analysis,
            'processed': self.processed,
            'processing_status': self.processing_status,
            'created_at': self.created_at.isoformat()
        }
    
    def __repr__(self):
        return f'<Document {self.filename}>'

class ChatSession(db.Model):
    """Chat session model for AI conversations"""
    __tablename__ = 'chat_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    session_title = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    messages = db.relationship('ChatMessage', backref='session', lazy=True, order_by='ChatMessage.created_at')
    
    def to_dict(self):
        """Convert session to dictionary"""
        return {
            'id': self.id,
            'session_title': self.session_title,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'message_count': len(self.messages),
            'is_active': self.is_active
        }
    
    def __repr__(self):
        return f'<ChatSession {self.id}: {self.session_title}>'

class ChatMessage(db.Model):
    """Individual chat message model"""
    __tablename__ = 'chat_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('chat_sessions.id'), nullable=False)
    message_type = db.Column(db.String(20), nullable=False)  # 'user' or 'assistant'
    content = db.Column(db.Text, nullable=False)
    message_metadata = db.Column(db.Text, nullable=True)  # JSON string for additional data
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_metadata(self, metadata_dict):
        """Set metadata as JSON string"""
        self.message_metadata = json.dumps(metadata_dict)
    
    def get_metadata(self):
        """Get metadata as dictionary"""
        if self.message_metadata:
            return json.loads(self.message_metadata)
        return {}
    
    def to_dict(self):
        """Convert message to dictionary"""
        return {
            'id': self.id,
            'message_type': self.message_type,
            'content': self.content,
            'metadata': self.get_metadata(),
            'created_at': self.created_at.isoformat()
        }
    
    def __repr__(self):
        return f'<ChatMessage {self.id}: {self.message_type}>'

class LawyerConnection(db.Model):
    """Model for lawyer-client connections"""
    __tablename__ = 'lawyer_connections'
    
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    lawyer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    connection_status = db.Column(db.String(20), default='pending')  # 'pending', 'accepted', 'declined'
    case_description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    client = db.relationship('User', foreign_keys=[client_id], backref='client_connections')
    lawyer = db.relationship('User', foreign_keys=[lawyer_id], backref='lawyer_connections')
    
    def to_dict(self):
        """Convert connection to dictionary"""
        return {
            'id': self.id,
            'client_id': self.client_id,
            'lawyer_id': self.lawyer_id,
            'connection_status': self.connection_status,
            'case_description': self.case_description,
            'created_at': self.created_at.isoformat(),
            'client_name': self.client.name if self.client else None,
            'lawyer_name': self.lawyer.name if self.lawyer else None
        }
    
    def __repr__(self):
        return f'<LawyerConnection {self.id}: {self.connection_status}>'