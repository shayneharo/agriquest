"""
Student API endpoints for React frontend integration
"""

from flask import Blueprint, jsonify, session, request
from functools import wraps
from ..models.class_model import Class
from ..models.user import User

student_api_bp = Blueprint('student_api', __name__, url_prefix='/api/student')

def login_required(f):
    """Decorator to require login for API endpoints"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

@student_api_bp.route('/classes')
@login_required
def get_student_classes():
    """Get student's enrolled classes"""
    try:
        user_id = session['user_id']
        role = session.get('role')
        
        if role != 'student':
            return jsonify({'error': 'Access denied. Student role required.'}), 403
        
        classes = Class.get_classes_for_student(user_id)
        
        # Convert to JSON-serializable format
        classes_data = []
        for class_item in classes:
            class_data = {
                'id': class_item['id'],
                'name': class_item['name'],
                'description': class_item['description'],
                'status': class_item['status'],
                'approved_at': class_item['approved_at'],
                'enrolled_at': class_item['enrolled_at']
            }
            classes_data.append(class_data)
        
        return jsonify({
            'success': True,
            'classes': classes_data
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@student_api_bp.route('/enrollment-status')
@login_required
def get_enrollment_status():
    """Check if student is enrolled in any class"""
    try:
        user_id = session['user_id']
        role = session.get('role')
        
        if role != 'student':
            return jsonify({'error': 'Access denied. Student role required.'}), 403
        
        classes = Class.get_classes_for_student(user_id)
        is_enrolled = len(classes) > 0
        
        return jsonify({
            'success': True,
            'is_enrolled': is_enrolled,
            'enrolled_classes_count': len(classes)
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@student_api_bp.route('/profile')
@login_required
def get_student_profile():
    """Get student profile information"""
    try:
        user_id = session['user_id']
        user = User.get_user_by_id(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        profile_data = {
            'id': user['id'],
            'username': user['username'],
            'email': user['email'],
            'full_name': user['full_name'],
            'role': user['role'],
            'profile_picture': user.get('profile_picture')
        }
        
        return jsonify({
            'success': True,
            'profile': profile_data
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
