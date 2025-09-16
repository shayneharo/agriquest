"""
Role-Based Access Control (RBAC) Middleware for AgriQuest v2.0

This module provides decorators and middleware for implementing role-based
access control across the API endpoints. It ensures that only authorized
users can access specific endpoints based on their roles.

Classes:
    None

Functions:
    require_auth: Decorator to require authentication
    require_role: Decorator to require specific role(s)
    require_admin: Decorator to require admin role
    require_teacher: Decorator to require teacher role
    require_student: Decorator to require student role
    get_current_user: Get current authenticated user

Author: AgriQuest Development Team
Version: 2.0
"""

from functools import wraps
from flask import request, jsonify, session
from ..models.user import User

def require_auth(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        
        # Get current user
        user = User.get_user_by_id(session['user_id'])
        if not user:
            session.clear()
            return jsonify({'error': 'Invalid session'}), 401
        
        # Add user to kwargs for use in the function
        kwargs['current_user'] = user
        return f(*args, **kwargs)
    return decorated_function

def require_role(*roles):
    """Decorator to require specific role(s)"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                return jsonify({'error': 'Authentication required'}), 401
            
            user = User.get_user_by_id(session['user_id'])
            if not user:
                session.clear()
                return jsonify({'error': 'Invalid session'}), 401
            
            if user['role'] not in roles:
                return jsonify({'error': 'Insufficient permissions'}), 403
            
            kwargs['current_user'] = user
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def require_admin(f):
    """Decorator to require admin role"""
    return require_role('admin')(f)

def require_teacher(f):
    """Decorator to require teacher role"""
    return require_role('teacher', 'admin')(f)

def require_student(f):
    """Decorator to require student role"""
    return require_role('student')(f)

def get_current_user():
    """Get current authenticated user"""
    if 'user_id' not in session:
        return None
    
    user = User.get_user_by_id(session['user_id'])
    return user if user else None

def is_admin(user):
    """Check if user is admin"""
    return user and user.get('role') == 'admin'

def is_teacher(user):
    """Check if user is teacher or admin"""
    return user and user.get('role') in ['teacher', 'admin']

def is_student(user):
    """Check if user is student"""
    return user and user.get('role') == 'student'

def can_manage_subject(user, subject_id):
    """Check if user can manage a specific subject"""
    if not user:
        return False
    
    # Admin can manage all subjects
    if user['role'] == 'admin':
        return True
    
    # Teacher can manage subjects they're assigned to
    if user['role'] == 'teacher':
        from ..models.subject_teacher import SubjectTeacher
        teacher_subjects = SubjectTeacher.get_teacher_subjects(user['id'])
        return any(subject['id'] == subject_id for subject in teacher_subjects)
    
    return False

def can_access_subject(user, subject_id):
    """Check if user can access a specific subject"""
    if not user:
        return False
    
    # Admin and teachers can access all subjects
    if user['role'] in ['admin', 'teacher']:
        return True
    
    # Students can only access subjects they're enrolled in
    if user['role'] == 'student':
        from ..models.student_subject import StudentSubject
        return StudentSubject.is_student_enrolled(user['id'], subject_id)
    
    return False

