"""
Lawyer Network API Blueprint
Handles lawyer profiles, client connections, and networking features
"""
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from backend.models import db, User, LawyerConnection
from config import Config
import logging
from datetime import datetime
from sqlalchemy import or_, and_

logger = logging.getLogger(__name__)

lawyers_bp = Blueprint('lawyers', __name__)

@lawyers_bp.route('/search', methods=['GET'])
@login_required
def search_lawyers():
    """Search for lawyers based on criteria"""
    try:
        # Get query parameters
        specialization = request.args.get('specialization', '')
        location = request.args.get('location', '')
        experience = request.args.get('experience', '')
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 10)), 50)
        
        # Build query
        query = User.query.filter_by(user_type='lawyer', is_active=True)
        
        # Apply filters
        if specialization:
            query = query.filter(
                or_(
                    User.degree.ilike(f'%{specialization}%'),
                    User.qualifications.ilike(f'%{specialization}%')
                )
            )
        
        if location:
            query = query.filter(User.college.ilike(f'%{location}%'))
        
        # Execute query with pagination
        lawyers = query.offset((page - 1) * per_page).limit(per_page).all()
        total = query.count()
        
        # Format response
        lawyer_list = []
        for lawyer in lawyers:
            lawyer_data = lawyer.to_dict()
            # Remove sensitive information
            lawyer_data.pop('email', None)
            lawyer_list.append(lawyer_data)
        
        return jsonify({
            'success': True,
            'lawyers': lawyer_list,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': (total + per_page - 1) // per_page
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Search lawyers error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to search lawyers'
        }), 500

@lawyers_bp.route('/profile/<int:lawyer_id>', methods=['GET'])
@login_required
def get_lawyer_profile(lawyer_id):
    """Get lawyer's public profile"""
    try:
        lawyer = User.query.filter_by(
            id=lawyer_id,
            user_type='lawyer',
            is_active=True
        ).first()
        
        if not lawyer:
            return jsonify({
                'success': False,
                'message': 'Lawyer not found'
            }), 404
        
        # Get lawyer's profile (without sensitive data)
        profile = lawyer.to_dict()
        profile.pop('email', None)
        
        # Get connection status if user is not the lawyer
        connection_status = None
        if current_user.id != lawyer_id:
            connection = LawyerConnection.query.filter_by(
                client_id=current_user.id,
                lawyer_id=lawyer_id
            ).first()
            connection_status = connection.connection_status if connection else None
        
        return jsonify({
            'success': True,
            'lawyer': profile,
            'connection_status': connection_status
        }), 200
        
    except Exception as e:
        logger.error(f"Get lawyer profile error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to fetch lawyer profile'
        }), 500

@lawyers_bp.route('/connect', methods=['POST'])
@login_required
def connect_with_lawyer():
    """Send connection request to lawyer"""
    try:
        data = request.get_json()
        lawyer_id = data.get('lawyer_id')
        case_description = data.get('case_description', '').strip()
        
        if not lawyer_id:
            return jsonify({
                'success': False,
                'message': 'Lawyer ID is required'
            }), 400
        
        # Prevent self-connection
        if current_user.id == lawyer_id:
            return jsonify({
                'success': False,
                'message': 'Cannot connect with yourself'
            }), 400
        
        # Verify lawyer exists
        lawyer = User.query.filter_by(
            id=lawyer_id,
            user_type='lawyer',
            is_active=True
        ).first()
        
        if not lawyer:
            return jsonify({
                'success': False,
                'message': 'Lawyer not found'
            }), 404
        
        # Check if connection already exists
        existing_connection = LawyerConnection.query.filter_by(
            client_id=current_user.id,
            lawyer_id=lawyer_id
        ).first()
        
        if existing_connection:
            return jsonify({
                'success': False,
                'message': f'Connection already exists with status: {existing_connection.connection_status}'
            }), 409
        
        # Create new connection
        connection = LawyerConnection(
            client_id=current_user.id,
            lawyer_id=lawyer_id,
            case_description=case_description,
            connection_status='pending'
        )
        
        db.session.add(connection)
        db.session.commit()
        
        logger.info(f"Connection request sent: Client {current_user.id} to Lawyer {lawyer_id}")
        
        return jsonify({
            'success': True,
            'message': 'Connection request sent successfully',
            'connection': connection.to_dict()
        }), 201
        
    except Exception as e:
        logger.error(f"Connect with lawyer error: {str(e)}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Failed to send connection request'
        }), 500

@lawyers_bp.route('/connections', methods=['GET'])
@login_required
def get_connections():
    """Get user's connections (different for lawyers and clients)"""
    try:
        if current_user.user_type == 'lawyer':
            # Get connections where user is the lawyer
            connections = LawyerConnection.query.filter_by(
                lawyer_id=current_user.id
            ).order_by(LawyerConnection.created_at.desc()).all()
        else:
            # Get connections where user is the client
            connections = LawyerConnection.query.filter_by(
                client_id=current_user.id
            ).order_by(LawyerConnection.created_at.desc()).all()
        
        return jsonify({
            'success': True,
            'connections': [conn.to_dict() for conn in connections]
        }), 200
        
    except Exception as e:
        logger.error(f"Get connections error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to fetch connections'
        }), 500

@lawyers_bp.route('/connections/<int:connection_id>/respond', methods=['PUT'])
@login_required
def respond_to_connection(connection_id):
    """Respond to connection request (for lawyers)"""
    try:
        data = request.get_json()
        response = data.get('response', '').lower()
        
        if response not in ['accepted', 'declined']:
            return jsonify({
                'success': False,
                'message': 'Response must be either "accepted" or "declined"'
            }), 400
        
        # Find connection
        connection = LawyerConnection.query.filter_by(
            id=connection_id,
            lawyer_id=current_user.id
        ).first()
        
        if not connection:
            return jsonify({
                'success': False,
                'message': 'Connection request not found'
            }), 404
        
        if connection.connection_status != 'pending':
            return jsonify({
                'success': False,
                'message': f'Connection already {connection.connection_status}'
            }), 409
        
        # Update connection status
        connection.connection_status = response
        connection.updated_at = datetime.utcnow()
        db.session.commit()
        
        logger.info(f"Connection {connection_id} {response} by lawyer {current_user.id}")
        
        return jsonify({
            'success': True,
            'message': f'Connection request {response}',
            'connection': connection.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Respond to connection error: {str(e)}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Failed to respond to connection request'
        }), 500

@lawyers_bp.route('/stats', methods=['GET'])
@login_required
def get_lawyer_stats():
    """Get lawyer statistics (for lawyer dashboard)"""
    try:
        if current_user.user_type != 'lawyer':
            return jsonify({
                'success': False,
                'message': 'Access denied. Lawyers only.'
            }), 403
        
        # Get connection statistics
        total_requests = LawyerConnection.query.filter_by(
            lawyer_id=current_user.id
        ).count()
        
        pending_requests = LawyerConnection.query.filter_by(
            lawyer_id=current_user.id,
            connection_status='pending'
        ).count()
        
        accepted_connections = LawyerConnection.query.filter_by(
            lawyer_id=current_user.id,
            connection_status='accepted'
        ).count()
        
        # Get recent connections
        recent_connections = LawyerConnection.query.filter_by(
            lawyer_id=current_user.id
        ).order_by(LawyerConnection.created_at.desc()).limit(5).all()
        
        stats = {
            'total_requests': total_requests,
            'pending_requests': pending_requests,
            'accepted_connections': accepted_connections,
            'recent_connections': [conn.to_dict() for conn in recent_connections]
        }
        
        return jsonify({
            'success': True,
            'stats': stats
        }), 200
        
    except Exception as e:
        logger.error(f"Get lawyer stats error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to fetch statistics'
        }), 500

@lawyers_bp.route('/specializations', methods=['GET'])
def get_specializations():
    """Get available legal specializations"""
    specializations = [
        {
            'id': 'criminal',
            'name': 'Criminal Law',
            'description': 'Criminal defense, prosecution, bail matters'
        },
        {
            'id': 'civil',
            'name': 'Civil Law',
            'description': 'Civil disputes, contracts, property matters'
        },
        {
            'id': 'family',
            'name': 'Family Law',
            'description': 'Marriage, divorce, custody, maintenance'
        },
        {
            'id': 'corporate',
            'name': 'Corporate Law',
            'description': 'Company law, mergers, compliance'
        },
        {
            'id': 'intellectual_property',
            'name': 'Intellectual Property',
            'description': 'Patents, trademarks, copyrights'
        },
        {
            'id': 'tax',
            'name': 'Tax Law',
            'description': 'Income tax, GST, tax planning'
        },
        {
            'id': 'labor',
            'name': 'Labor Law',
            'description': 'Employment disputes, labor compliance'
        },
        {
            'id': 'real_estate',
            'name': 'Real Estate Law',
            'description': 'Property transactions, real estate disputes'
        }
    ]
    
    return jsonify({
        'success': True,
        'specializations': specializations
    }), 200

@lawyers_bp.route('/featured', methods=['GET'])
def get_featured_lawyers():
    """Get featured lawyers for homepage"""
    try:
        # Get lawyers with most connections (simplified featured logic)
        featured_lawyers = db.session.query(User)\
            .filter_by(user_type='lawyer', is_active=True)\
            .limit(6).all()
        
        lawyer_list = []
        for lawyer in featured_lawyers:
            lawyer_data = lawyer.to_dict()
            # Remove sensitive information
            lawyer_data.pop('email', None)
            
            # Add connection count
            connection_count = LawyerConnection.query.filter_by(
                lawyer_id=lawyer.id,
                connection_status='accepted'
            ).count()
            lawyer_data['connection_count'] = connection_count
            
            lawyer_list.append(lawyer_data)
        
        return jsonify({
            'success': True,
            'featured_lawyers': lawyer_list
        }), 200
        
    except Exception as e:
        logger.error(f"Get featured lawyers error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to fetch featured lawyers'
        }), 500

@lawyers_bp.route('/directory', methods=['GET'])
def get_lawyer_directory():
    """Get lawyer directory with filters"""
    try:
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 12)), 50)
        
        # Get all active lawyers
        query = User.query.filter_by(user_type='lawyer', is_active=True)
        
        # Apply pagination
        lawyers = query.offset((page - 1) * per_page).limit(per_page).all()
        total = query.count()
        
        # Format response
        lawyer_list = []
        for lawyer in lawyers:
            lawyer_data = lawyer.to_dict()
            # Remove sensitive information
            lawyer_data.pop('email', None)
            
            # Add connection statistics
            total_connections = LawyerConnection.query.filter_by(
                lawyer_id=lawyer.id
            ).count()
            lawyer_data['total_connections'] = total_connections
            
            lawyer_list.append(lawyer_data)
        
        return jsonify({
            'success': True,
            'lawyers': lawyer_list,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': (total + per_page - 1) // per_page
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Get lawyer directory error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to fetch lawyer directory'
        }), 500