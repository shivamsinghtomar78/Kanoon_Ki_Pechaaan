"""
AI Chatbot API Blueprint
Handles legal AI assistance and chat functionality
"""
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from backend.models import db, ChatSession, ChatMessage
from config import Config
import logging
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, AIMessage
from datetime import datetime
import json

logger = logging.getLogger(__name__)

chatbot_bp = Blueprint('chatbot', __name__)

class LegalAI:
    """Legal AI assistant using Google Gemini"""
    
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-pro",
            google_api_key=Config.GOOGLE_API_KEY,
            temperature=0.3
        )
        self.system_prompt = """You are a specialized AI assistant for Indian legal matters. 
        You have expertise in:
        - Indian Penal Code (IPC)
        - Code of Criminal Procedure (CrPC)
        - Constitution of India
        - Civil Procedure Code (CPC)
        - Contract Law
        - Property Law
        - Family Law
        - Corporate Law
        
        Provide accurate, helpful legal information while emphasizing that users should consult qualified lawyers for specific legal advice.
        Always cite relevant sections and case laws when possible.
        Keep responses clear, structured, and professional."""
    
    def get_legal_response(self, user_query, chat_history=None):
        """Get AI response for legal query"""
        try:
            # Prepare messages
            messages = [HumanMessage(content=self.system_prompt)]
            
            # Add chat history if available
            if chat_history:
                for msg in chat_history[-10:]:  # Last 10 messages for context
                    if msg.message_type == 'user':
                        messages.append(HumanMessage(content=msg.content))
                    else:
                        messages.append(AIMessage(content=msg.content))
            
            # Add current query
            messages.append(HumanMessage(content=user_query))
            
            # Get AI response
            response = self.llm.invoke(messages)
            
            return {
                'success': True,
                'response': response.content,
                'sources': self._extract_sources(response.content)
            }
            
        except Exception as e:
            logger.error(f"AI response error: {str(e)}")
            return {
                'success': False,
                'error': 'Failed to generate AI response'
            }
    
    def _extract_sources(self, response_text):
        """Extract legal sources mentioned in response"""
        sources = []
        # Simple keyword matching for legal sources
        legal_keywords = [
            'IPC', 'CrPC', 'Constitution', 'CPC', 'Section',
            'Article', 'Act', 'Supreme Court', 'High Court'
        ]
        
        for keyword in legal_keywords:
            if keyword.lower() in response_text.lower():
                sources.append(keyword)
        
        return list(set(sources))

# Initialize AI assistant
legal_ai = LegalAI()

@chatbot_bp.route('/sessions', methods=['GET'])
@login_required
def get_chat_sessions():
    """Get user's chat sessions"""
    try:
        sessions = ChatSession.query.filter_by(
            user_id=current_user.id,
            is_active=True
        ).order_by(ChatSession.updated_at.desc()).all()
        
        return jsonify({
            'success': True,
            'sessions': [session.to_dict() for session in sessions]
        }), 200
        
    except Exception as e:
        logger.error(f"Get sessions error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to fetch chat sessions'
        }), 500

@chatbot_bp.route('/sessions', methods=['POST'])
@login_required
def create_chat_session():
    """Create new chat session"""
    try:
        data = request.get_json()
        title = data.get('title', f"Chat Session {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        
        session = ChatSession(
            user_id=current_user.id,
            session_title=title
        )
        
        db.session.add(session)
        db.session.commit()
        
        logger.info(f"New chat session created: {session.id}")
        
        return jsonify({
            'success': True,
            'session': session.to_dict()
        }), 201
        
    except Exception as e:
        logger.error(f"Create session error: {str(e)}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Failed to create chat session'
        }), 500

@chatbot_bp.route('/sessions/<int:session_id>/messages', methods=['GET'])
@login_required
def get_chat_messages(session_id):
    """Get messages from a chat session"""
    try:
        session = ChatSession.query.filter_by(
            id=session_id,
            user_id=current_user.id
        ).first()
        
        if not session:
            return jsonify({
                'success': False,
                'message': 'Chat session not found'
            }), 404
        
        messages = ChatMessage.query.filter_by(
            session_id=session_id
        ).order_by(ChatMessage.created_at.asc()).all()
        
        return jsonify({
            'success': True,
            'messages': [msg.to_dict() for msg in messages],
            'session': session.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Get messages error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to fetch messages'
        }), 500

@chatbot_bp.route('/sessions/<int:session_id>/chat', methods=['POST'])
@login_required
def send_chat_message(session_id):
    """Send message and get AI response"""
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({
                'success': False,
                'message': 'Message cannot be empty'
            }), 400
        
        # Verify session ownership
        session = ChatSession.query.filter_by(
            id=session_id,
            user_id=current_user.id
        ).first()
        
        if not session:
            return jsonify({
                'success': False,
                'message': 'Chat session not found'
            }), 404
        
        # Get chat history for context
        chat_history = ChatMessage.query.filter_by(
            session_id=session_id
        ).order_by(ChatMessage.created_at.asc()).all()
        
        # Save user message
        user_msg = ChatMessage(
            session_id=session_id,
            message_type='user',
            content=user_message
        )
        db.session.add(user_msg)
        
        # Get AI response
        ai_result = legal_ai.get_legal_response(user_message, chat_history)
        
        if ai_result['success']:
            # Save AI response
            ai_msg = ChatMessage(
                session_id=session_id,
                message_type='assistant',
                content=ai_result['response']
            )
            ai_msg.set_metadata({
                'sources': ai_result.get('sources', []),
                'timestamp': datetime.utcnow().isoformat()
            })
            db.session.add(ai_msg)
            
            # Update session timestamp
            session.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'user_message': user_msg.to_dict(),
                'ai_response': ai_msg.to_dict()
            }), 200
        else:
            # Save error message
            error_msg = ChatMessage(
                session_id=session_id,
                message_type='assistant',
                content="I apologize, but I'm having trouble processing your request right now. Please try again."
            )
            db.session.add(error_msg)
            db.session.commit()
            
            return jsonify({
                'success': False,
                'message': 'AI service temporarily unavailable',
                'user_message': user_msg.to_dict(),
                'error_response': error_msg.to_dict()
            }), 503
        
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Failed to process chat message'
        }), 500

@chatbot_bp.route('/sessions/<int:session_id>', methods=['DELETE'])
@login_required
def delete_chat_session(session_id):
    """Delete chat session"""
    try:
        session = ChatSession.query.filter_by(
            id=session_id,
            user_id=current_user.id
        ).first()
        
        if not session:
            return jsonify({
                'success': False,
                'message': 'Chat session not found'
            }), 404
        
        # Mark as inactive instead of hard delete
        session.is_active = False
        db.session.commit()
        
        logger.info(f"Chat session deleted: {session_id}")
        
        return jsonify({
            'success': True,
            'message': 'Chat session deleted successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Delete session error: {str(e)}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Failed to delete chat session'
        }), 500

@chatbot_bp.route('/quick-question', methods=['POST'])
@login_required
def quick_legal_question():
    """Quick legal question without session"""
    try:
        data = request.get_json()
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({
                'success': False,
                'message': 'Question cannot be empty'
            }), 400
        
        # Get AI response
        ai_result = legal_ai.get_legal_response(question)
        
        if ai_result['success']:
            return jsonify({
                'success': True,
                'question': question,
                'response': ai_result['response'],
                'sources': ai_result.get('sources', [])
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to get AI response'
            }), 503
        
    except Exception as e:
        logger.error(f"Quick question error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to process question'
        }), 500

@chatbot_bp.route('/legal-categories', methods=['GET'])
def get_legal_categories():
    """Get available legal categories for guidance"""
    categories = [
        {
            'id': 'criminal',
            'name': 'Criminal Law',
            'description': 'IPC, CrPC, criminal procedures',
            'examples': ['Theft', 'Assault', 'Fraud', 'Bail procedures']
        },
        {
            'id': 'civil',
            'name': 'Civil Law',
            'description': 'CPC, civil procedures, contracts',
            'examples': ['Contract disputes', 'Property disputes', 'Tort claims']
        },
        {
            'id': 'family',
            'name': 'Family Law',
            'description': 'Marriage, divorce, custody',
            'examples': ['Divorce procedures', 'Child custody', 'Maintenance']
        },
        {
            'id': 'corporate',
            'name': 'Corporate Law',
            'description': 'Company law, business regulations',
            'examples': ['Company registration', 'Compliance', 'Corporate governance']
        },
        {
            'id': 'constitutional',
            'name': 'Constitutional Law',
            'description': 'Fundamental rights, constitutional matters',
            'examples': ['Fundamental rights', 'Writ petitions', 'Constitutional provisions']
        }
    ]
    
    return jsonify({
        'success': True,
        'categories': categories
    }), 200