"""
Authentication API for AgriQuest v2.0

This module provides REST API endpoints for user authentication including
login, registration, logout, password change, and profile management.

Endpoints:
    POST /api/auth/login - User login
    POST /api/auth/register - User registration (teacher, student only)
    POST /api/auth/logout - User logout
    POST /api/auth/change-password - Change password
    GET /api/auth/profile - View profile

Author: AgriQuest Development Team
Version: 2.0
"""

from flask import Blueprint, request, jsonify, session
from werkzeug.security import check_password_hash
from ..models.user import User
from ..middleware.rbac import require_auth
from ..utils.otp_utils import send_otp_email
import re

auth_api = Blueprint('auth_api', __name__, url_prefix='/api/auth')

@auth_api.route('/login', methods=['POST'])
def login():
    """User login endpoint"""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        if not username or not password:
            return jsonify({'error': 'Username and password are required'}), 400
        
        # Get user from database
        user = User.get_user_by_username(username)
        if not user:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Check if user is active
        if not user.get('is_active', True):
            return jsonify({'error': 'Account is deactivated'}), 401
        
        # Verify password
        if not check_password_hash(user['password'], password):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Update last login
        User.update_last_login(user['id'])
        
        # Create session
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['role'] = user['role']
        
        return jsonify({
            'message': 'Login successful',
            'user': {
                'id': user['id'],
                'username': user['username'],
                'role': user['role'],
                'full_name': user.get('full_name'),
                'email': user.get('email')
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Login failed: {str(e)}'}), 500

@auth_api.route('/register', methods=['POST'])
def register():
    """User registration endpoint (teacher, student only)"""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '')
        role = data.get('role', 'student')
        email = data.get('email', '').strip()
        full_name = data.get('full_name', '').strip()
        
        # Validate role
        if role not in ['teacher', 'student']:
            return jsonify({'error': 'Invalid role. Only teacher and student roles are allowed'}), 400
        
        # Validate required fields
        if not username or not password or not email:
            return jsonify({'error': 'Username, password, and email are required'}), 400
        
        # Validate username format
        if len(username) < 3 or len(username) > 50:
            return jsonify({'error': 'Username must be between 3 and 50 characters'}), 400
        
        # Validate password strength
        if len(password) < 8:
            return jsonify({'error': 'Password must be at least 8 characters long'}), 400
        
        if not re.search(r'[A-Z]', password):
            return jsonify({'error': 'Password must contain at least one uppercase letter'}), 400
        
        if not re.search(r'[a-z]', password):
            return jsonify({'error': 'Password must contain at least one lowercase letter'}), 400
        
        if not re.search(r'\d', password):
            return jsonify({'error': 'Password must contain at least one number'}), 400
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return jsonify({'error': 'Password must contain at least one special character'}), 400
        
        # Validate email format
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Check if username already exists
        if User.get_user_by_username(username):
            return jsonify({'error': 'Username already exists'}), 409
        
        # Check if email already exists
        if User.get_user_by_email(email):
            return jsonify({'error': 'Email already exists'}), 409
        
        # Create user
        success = User.create_user(
            username=username,
            password=password,
            role=role,
            email=email,
            full_name=full_name or username
        )
        
        if success:
            return jsonify({'message': 'Registration successful'}), 201
        else:
            return jsonify({'error': 'Registration failed'}), 500
            
    except Exception as e:
        return jsonify({'error': f'Registration failed: {str(e)}'}), 500

@auth_api.route('/logout', methods=['POST'])
@require_auth
def logout(current_user):
    """User logout endpoint"""
    try:
        session.clear()
        return jsonify({'message': 'Logout successful'}), 200
    except Exception as e:
        return jsonify({'error': f'Logout failed: {str(e)}'}), 500

@auth_api.route('/change-password', methods=['POST'])
@require_auth
def change_password(current_user):
    """Change password endpoint"""
    try:
        data = request.get_json()
        current_password = data.get('current_password', '')
        new_password = data.get('new_password', '')
        
        if not current_password or not new_password:
            return jsonify({'error': 'Current password and new password are required'}), 400
        
        # Validate new password strength
        if len(new_password) < 8:
            return jsonify({'error': 'New password must be at least 8 characters long'}), 400
        
        if not re.search(r'[A-Z]', new_password):
            return jsonify({'error': 'New password must contain at least one uppercase letter'}), 400
        
        if not re.search(r'[a-z]', new_password):
            return jsonify({'error': 'New password must contain at least one lowercase letter'}), 400
        
        if not re.search(r'\d', new_password):
            return jsonify({'error': 'New password must contain at least one number'}), 400
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', new_password):
            return jsonify({'error': 'New password must contain at least one special character'}), 400
        
        # Change password
        success, message = User.change_password(
            current_user['id'],
            current_password,
            new_password
        )
        
        if success:
            return jsonify({'message': message}), 200
        else:
            return jsonify({'error': message}), 400
            
    except Exception as e:
        return jsonify({'error': f'Password change failed: {str(e)}'}), 500

@auth_api.route('/profile', methods=['GET'])
@require_auth
def get_profile(current_user):
    """Get user profile endpoint"""
    try:
        return jsonify({
            'user': {
                'id': current_user['id'],
                'username': current_user['username'],
                'role': current_user['role'],
                'full_name': current_user.get('full_name'),
                'email': current_user.get('email'),
                'profile_picture': current_user.get('profile_picture'),
                'last_login': current_user.get('last_login'),
                'created_at': current_user.get('created_at')
            }
        }), 200
    except Exception as e:
        return jsonify({'error': f'Failed to get profile: {str(e)}'}), 500

@auth_api.route('/profile', methods=['PUT'])
@require_auth
def update_profile(current_user):
    """Update user profile endpoint"""
    try:
        data = request.get_json()
        full_name = data.get('full_name', '').strip()
        email = data.get('email', '').strip()
        
        # Validate email format if provided
        if email:
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, email):
                return jsonify({'error': 'Invalid email format'}), 400
            
            # Check if email is already taken by another user
            existing_user = User.get_user_by_email(email)
            if existing_user and existing_user['id'] != current_user['id']:
                return jsonify({'error': 'Email already exists'}), 409
        
        # Update profile
        success = User.update_profile(
            current_user['id'],
            full_name=full_name or None,
            email=email or None
        )
        
        if success:
            return jsonify({'message': 'Profile updated successfully'}), 200
        else:
            return jsonify({'error': 'Profile update failed'}), 500
            
    except Exception as e:
        return jsonify({'error': f'Profile update failed: {str(e)}'}), 500

