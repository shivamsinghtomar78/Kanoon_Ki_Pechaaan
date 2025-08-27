"""
Document Analysis API Blueprint
Handles document upload, processing, and analysis
"""
from flask import Blueprint, request, jsonify, send_file
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from backend.models import db, Document
from config import Config
import logging
import os
import uuid
from datetime import datetime
import PyPDF2
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
import json

logger = logging.getLogger(__name__)

documents_bp = Blueprint('documents', __name__)

# Configure upload settings
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

class DocumentAnalyzer:
    """Document analysis using AI"""
    
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-pro",
            google_api_key=Config.GOOGLE_API_KEY,
            temperature=0.1
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=2000,
            chunk_overlap=200
        )
    
    def extract_text_from_pdf(self, file_path):
        """Extract text from PDF file"""
        try:
            text = ""
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            logger.error(f"PDF extraction error: {str(e)}")
            return None
    
    def extract_text_from_txt(self, file_path):
        """Extract text from text file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            logger.error(f"Text extraction error: {str(e)}")
            return None
    
    def analyze_document(self, text, document_type="legal"):
        """Analyze document content using AI"""
        try:
            # Create analysis prompt
            prompt = f"""
            Analyze the following {document_type} document and provide:
            1. A comprehensive summary (2-3 paragraphs)
            2. Key legal points (as a list)
            3. Important sections or clauses
            4. Legal implications or considerations
            5. Recommendations or next steps
            
            Document text:
            {text[:8000]}  # Limit text for API
            
            Provide the response in the following JSON format:
            {{
                "summary": "detailed summary here",
                "key_points": ["point 1", "point 2", "point 3"],
                "important_sections": ["section 1", "section 2"],
                "legal_implications": "legal implications text",
                "recommendations": "recommendations text"
            }}
            """
            
            response = self.llm.invoke(prompt)
            
            # Try to parse JSON response
            try:
                analysis = json.loads(response.content)
                return {
                    'success': True,
                    'analysis': analysis
                }
            except json.JSONDecodeError:
                # Fallback to text response
                return {
                    'success': True,
                    'analysis': {
                        'summary': response.content,
                        'key_points': [],
                        'important_sections': [],
                        'legal_implications': "",
                        'recommendations': ""
                    }
                }
            
        except Exception as e:
            logger.error(f"Document analysis error: {str(e)}")
            return {
                'success': False,
                'error': 'Failed to analyze document'
            }

# Initialize document analyzer
doc_analyzer = DocumentAnalyzer()

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_file_extension(filename):
    """Get file extension"""
    return filename.rsplit('.', 1)[1].lower() if '.' in filename else ''

@documents_bp.route('/upload', methods=['POST'])
@login_required
def upload_document():
    """Upload and process document"""
    try:
        # Check if file is in request
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'message': 'No file provided'
            }), 400
        
        file = request.files['file']
        
        # Check if file is selected
        if file.filename == '':
            return jsonify({
                'success': False,
                'message': 'No file selected'
            }), 400
        
        # Validate file
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'message': f'File type not allowed. Supported: {", ".join(ALLOWED_EXTENSIONS)}'
            }), 400
        
        # Check file size (rough check)
        file.seek(0, 2)  # Seek to end
        file_size = file.tell()
        file.seek(0)  # Reset to beginning
        
        if file_size > MAX_FILE_SIZE:
            return jsonify({
                'success': False,
                'message': f'File too large. Maximum size: {MAX_FILE_SIZE // (1024*1024)}MB'
            }), 400
        
        # Generate unique filename
        original_filename = secure_filename(file.filename)
        file_extension = get_file_extension(original_filename)
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        
        # Ensure upload directory exists
        upload_dir = Config.UPLOAD_FOLDER
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save file
        file_path = os.path.join(upload_dir, unique_filename)
        file.save(file_path)
        
        # Create document record
        document = Document(
            user_id=current_user.id,
            filename=unique_filename,
            original_filename=original_filename,
            file_path=file_path,
            file_size=file_size,
            content_type=file.content_type or f'application/{file_extension}',
            processing_status='processing'
        )
        
        db.session.add(document)
        db.session.commit()
        
        # Process document in background (for now, do it synchronously)
        try:
            # Extract text based on file type
            if file_extension == 'pdf':
                extracted_text = doc_analyzer.extract_text_from_pdf(file_path)
            elif file_extension in ['txt']:
                extracted_text = doc_analyzer.extract_text_from_txt(file_path)
            else:
                extracted_text = "Document uploaded successfully. Text extraction not yet supported for this file type."
            
            if extracted_text:
                document.extracted_text = extracted_text
                
                # Analyze document
                analysis_result = doc_analyzer.analyze_document(extracted_text)
                
                if analysis_result['success']:
                    analysis = analysis_result['analysis']
                    document.summary = analysis.get('summary', '')
                    document.set_key_points(analysis.get('key_points', []))
                    document.legal_analysis = json.dumps({
                        'important_sections': analysis.get('important_sections', []),
                        'legal_implications': analysis.get('legal_implications', ''),
                        'recommendations': analysis.get('recommendations', '')
                    })
                
                document.processed = True
                document.processing_status = 'completed'
            else:
                document.processing_status = 'failed'
            
            db.session.commit()
            
        except Exception as process_error:
            logger.error(f"Document processing error: {str(process_error)}")
            document.processing_status = 'failed'
            db.session.commit()
        
        logger.info(f"Document uploaded: {original_filename} by user {current_user.id}")
        
        return jsonify({
            'success': True,
            'message': 'Document uploaded and processed successfully',
            'document': document.to_dict()
        }), 201
        
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        if 'document' in locals():
            db.session.rollback()
            # Clean up file if document creation failed
            if os.path.exists(file_path):
                os.remove(file_path)
        return jsonify({
            'success': False,
            'message': 'Failed to upload document'
        }), 500

@documents_bp.route('/', methods=['GET'])
@login_required
def get_documents():
    """Get user's documents"""
    try:
        documents = Document.query.filter_by(
            user_id=current_user.id
        ).order_by(Document.created_at.desc()).all()
        
        return jsonify({
            'success': True,
            'documents': [doc.to_dict() for doc in documents]
        }), 200
        
    except Exception as e:
        logger.error(f"Get documents error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to fetch documents'
        }), 500

@documents_bp.route('/<int:document_id>', methods=['GET'])
@login_required
def get_document(document_id):
    """Get specific document details"""
    try:
        document = Document.query.filter_by(
            id=document_id,
            user_id=current_user.id
        ).first()
        
        if not document:
            return jsonify({
                'success': False,
                'message': 'Document not found'
            }), 404
        
        return jsonify({
            'success': True,
            'document': document.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Get document error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to fetch document'
        }), 500

@documents_bp.route('/<int:document_id>/download', methods=['GET'])
@login_required
def download_document(document_id):
    """Download document file"""
    try:
        document = Document.query.filter_by(
            id=document_id,
            user_id=current_user.id
        ).first()
        
        if not document:
            return jsonify({
                'success': False,
                'message': 'Document not found'
            }), 404
        
        if not os.path.exists(document.file_path):
            return jsonify({
                'success': False,
                'message': 'Document file not found'
            }), 404
        
        return send_file(
            document.file_path,
            as_attachment=True,
            download_name=document.original_filename
        )
        
    except Exception as e:
        logger.error(f"Download error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to download document'
        }), 500

@documents_bp.route('/<int:document_id>', methods=['DELETE'])
@login_required
def delete_document(document_id):
    """Delete document"""
    try:
        document = Document.query.filter_by(
            id=document_id,
            user_id=current_user.id
        ).first()
        
        if not document:
            return jsonify({
                'success': False,
                'message': 'Document not found'
            }), 404
        
        # Delete file from filesystem
        if os.path.exists(document.file_path):
            os.remove(document.file_path)
        
        # Delete from database
        db.session.delete(document)
        db.session.commit()
        
        logger.info(f"Document deleted: {document_id}")
        
        return jsonify({
            'success': True,
            'message': 'Document deleted successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Delete document error: {str(e)}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Failed to delete document'
        }), 500

@documents_bp.route('/<int:document_id>/reprocess', methods=['POST'])
@login_required
def reprocess_document(document_id):
    """Reprocess document analysis"""
    try:
        document = Document.query.filter_by(
            id=document_id,
            user_id=current_user.id
        ).first()
        
        if not document:
            return jsonify({
                'success': False,
                'message': 'Document not found'
            }), 404
        
        if not os.path.exists(document.file_path):
            return jsonify({
                'success': False,
                'message': 'Document file not found'
            }), 404
        
        # Update processing status
        document.processing_status = 'processing'
        db.session.commit()
        
        # Re-extract and analyze
        file_extension = get_file_extension(document.original_filename)
        
        if file_extension == 'pdf':
            extracted_text = doc_analyzer.extract_text_from_pdf(document.file_path)
        elif file_extension in ['txt']:
            extracted_text = doc_analyzer.extract_text_from_txt(document.file_path)
        else:
            extracted_text = document.extracted_text
        
        if extracted_text:
            document.extracted_text = extracted_text
            
            # Re-analyze document
            analysis_result = doc_analyzer.analyze_document(extracted_text)
            
            if analysis_result['success']:
                analysis = analysis_result['analysis']
                document.summary = analysis.get('summary', '')
                document.set_key_points(analysis.get('key_points', []))
                document.legal_analysis = json.dumps({
                    'important_sections': analysis.get('important_sections', []),
                    'legal_implications': analysis.get('legal_implications', ''),
                    'recommendations': analysis.get('recommendations', '')
                })
            
            document.processed = True
            document.processing_status = 'completed'
        else:
            document.processing_status = 'failed'
        
        document.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Document reprocessed successfully',
            'document': document.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Reprocess error: {str(e)}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Failed to reprocess document'
        }), 500