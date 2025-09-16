"""
Classes API endpoints for React frontend integration
"""

from flask import Blueprint, jsonify, session, request
from functools import wraps
from ..models.class_model import Class
from ..models.user import User

classes_api_bp = Blueprint('classes_api', __name__, url_prefix='/api/classes')

def login_required(f):
    """Decorator to require login for API endpoints"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

@classes_api_bp.route('/')
@login_required
def get_all_classes():
    """Get all available classes"""
    try:
        classes = Class.get_all_classes()
        
        # Convert to JSON-serializable format
        classes_data = []
        for class_item in classes:
            class_data = {
                'id': class_item['id'],
                'name': class_item['name'],
                'description': class_item['description'],
                'created_at': class_item['created_at'],
                'teacher_count': class_item['teacher_count']
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

@classes_api_bp.route('/<int:class_id>/enroll', methods=['POST'])
@login_required
def enroll_in_class(class_id):
    """Enroll student in a class"""
    try:
        user_id = session['user_id']
        role = session.get('role')
        
        if role != 'student':
            return jsonify({'error': 'Access denied. Student role required.'}), 403
        
        # Check if class exists
        class_info = Class.get_class_by_id(class_id)
        if not class_info:
            return jsonify({'error': 'Class not found'}), 404
        
        # Check if already enrolled
        existing_enrollment = Class.get_student_enrollment_status(user_id, class_id)
        if existing_enrollment:
            if existing_enrollment['status'] == 'approved':
                return jsonify({'error': 'You are already enrolled in this class'}), 400
            elif existing_enrollment['status'] == 'pending':
                return jsonify({'error': 'Your enrollment request is already pending'}), 400
        
        # Enroll student
        success = Class.enroll_student(user_id, class_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Successfully enrolled in class. Waiting for teacher approval.'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to enroll in class'
            }), 500
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@classes_api_bp.route('/<int:class_id>')
@login_required
def get_class_details(class_id):
    """Get detailed information about a specific class"""
    try:
        class_info = Class.get_class_by_id(class_id)
        
        if not class_info:
            return jsonify({'error': 'Class not found'}), 404
        
        # Get teachers for this class
        teachers = Class.get_class_teachers(class_id)
        
        # Get enrollment status for current user
        user_id = session['user_id']
        enrollment_status = Class.get_student_enrollment_status(user_id, class_id)
        
        class_data = {
            'id': class_info['id'],
            'name': class_info['name'],
            'description': class_info['description'],
            'created_at': class_info['created_at'],
            'teacher_count': class_info['teacher_count'],
            'teachers': teachers,
            'enrollment_status': enrollment_status
        }
        
        return jsonify({
            'success': True,
            'class': class_data
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@classes_api_bp.route('/<int:class_id>/students')
@login_required
def get_class_students(class_id):
    """Get students enrolled in a class (teachers only)"""
    try:
        user_id = session['user_id']
        role = session.get('role')
        
        if role not in ['teacher', 'admin']:
            return jsonify({'error': 'Access denied. Teacher role required.'}), 403
        
        # Check if teacher is assigned to this class
        if not Class.is_teacher_of_class(user_id, class_id):
            return jsonify({'error': 'You are not assigned to this class'}), 403
        
        students = Class.get_students_in_class(class_id)
        
        return jsonify({
            'success': True,
            'students': students
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@classes_api_bp.route('/enrollment-requests')
@login_required
def get_enrollment_requests():
    """Get pending enrollment requests (teachers only)"""
    try:
        role = session.get('role')
        
        if role not in ['teacher', 'admin']:
            return jsonify({'error': 'Access denied. Teacher role required.'}), 403
        
        pending_requests = Class.get_pending_enrollments()
        
        return jsonify({
            'success': True,
            'requests': pending_requests
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@classes_api_bp.route('/approve-enrollment', methods=['POST'])
@login_required
def approve_enrollment():
    """Approve student enrollment (teachers only)"""
    try:
        role = session.get('role')
        
        if role not in ['teacher', 'admin']:
            return jsonify({'error': 'Access denied. Teacher role required.'}), 403
        
        data = request.get_json()
        student_id = data.get('student_id')
        class_id = data.get('class_id')
        
        if not student_id or not class_id:
            return jsonify({'error': 'Student ID and Class ID are required'}), 400
        
        success = Class.approve_student(student_id, class_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Student enrollment approved successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to approve enrollment'
            }), 500
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@classes_api_bp.route('/reject-enrollment', methods=['POST'])
@login_required
def reject_enrollment():
    """Reject student enrollment (teachers only)"""
    try:
        role = session.get('role')
        
        if role not in ['teacher', 'admin']:
            return jsonify({'error': 'Access denied. Teacher role required.'}), 403
        
        data = request.get_json()
        student_id = data.get('student_id')
        class_id = data.get('class_id')
        
        if not student_id or not class_id:
            return jsonify({'error': 'Student ID and Class ID are required'}), 400
        
        success = Class.reject_student(student_id, class_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Student enrollment rejected'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to reject enrollment'
            }), 500
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
