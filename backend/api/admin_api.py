"""
Admin API for AgriQuest v2.0

This module provides REST API endpoints for admin functionality including
user management, subject management, teacher invitations, student weakness
tracking, and notifications.

Endpoints:
    GET /api/admin/users - List all users
    POST /api/admin/users - Add new user
    DELETE /api/admin/users/:id - Remove user
    GET /api/admin/users/search - Search users
    GET /api/admin/subjects - List all subjects
    POST /api/admin/subjects - Create subject
    PUT /api/admin/subjects/:id - Update subject
    DELETE /api/admin/subjects/:id - Remove subject
    POST /api/admin/subjects/:id/invite-teacher - Invite teacher
    GET /api/admin/invitations - View invitations
    GET /api/admin/students/:id/weakness - View student weaknesses
    GET /api/admin/notifications - View notifications

Author: AgriQuest Development Team
Version: 2.0
"""

from flask import Blueprint, request, jsonify
from ..models.user import User
from ..models.subject import Subject
from ..models.subject_teacher import SubjectTeacher
from ..models.student_subject import StudentSubject
from ..models.weakness import Weakness
from ..models.notification import Notification
from ..middleware.rbac import require_admin
from werkzeug.security import generate_password_hash
import re

admin_api = Blueprint('admin_api', __name__, url_prefix='/api/admin')

# User Management Endpoints

@admin_api.route('/users', methods=['GET'])
@require_admin
def list_users(current_user):
    """List all users (teachers + students)"""
    try:
        role = request.args.get('role')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        
        if role and role in ['teacher', 'student']:
            users = User.get_users_by_role(role)
        else:
            users = User.get_all_users()
        
        # Simple pagination
        start = (page - 1) * per_page
        end = start + per_page
        paginated_users = users[start:end]
        
        return jsonify({
            'users': [dict(user) for user in paginated_users],
            'total': len(users),
            'page': page,
            'per_page': per_page,
            'total_pages': (len(users) + per_page - 1) // per_page
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to list users: {str(e)}'}), 500

@admin_api.route('/users', methods=['POST'])
@require_admin
def add_user(current_user):
    """Add new teacher/student"""
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
            # Create notification for the new user
            new_user = User.get_user_by_username(username)
            if new_user:
                Notification.create_notification(
                    new_user['id'],
                    'Account Created',
                    f'Your {role} account has been created successfully.',
                    'success'
                )
            
            return jsonify({'message': f'{role.title()} created successfully'}), 201
        else:
            return jsonify({'error': 'User creation failed'}), 500
            
    except Exception as e:
        return jsonify({'error': f'Failed to add user: {str(e)}'}), 500

@admin_api.route('/users/<int:user_id>', methods=['DELETE'])
@require_admin
def remove_user(current_user, user_id):
    """Remove teacher/student"""
    try:
        # Check if user exists
        user = User.get_user_by_id(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Prevent admin from deleting themselves
        if user_id == current_user['id']:
            return jsonify({'error': 'Cannot delete your own account'}), 400
        
        # Delete user
        User.delete_user(user_id)
        
        return jsonify({'message': 'User deleted successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to remove user: {str(e)}'}), 500

@admin_api.route('/users/search', methods=['GET'])
@require_admin
def search_users(current_user):
    """Search users"""
    try:
        query = request.args.get('query', '').strip()
        role = request.args.get('role')
        
        if not query:
            return jsonify({'error': 'Search query is required'}), 400
        
        users = User.search_users(query, role)
        
        return jsonify({
            'users': users,
            'total': len(users)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to search users: {str(e)}'}), 500

# Subject Management Endpoints

@admin_api.route('/subjects', methods=['GET'])
@require_admin
def list_subjects(current_user):
    """List all subjects"""
    try:
        subjects = Subject.get_all_subjects()
        return jsonify({'subjects': subjects}), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to list subjects: {str(e)}'}), 500

@admin_api.route('/subjects', methods=['POST'])
@require_admin
def create_subject(current_user):
    """Create subject"""
    try:
        data = request.get_json()
        name = data.get('name', '').strip()
        description = data.get('description', '').strip()
        year = data.get('year')
        code = data.get('code', '').strip()
        
        if not name:
            return jsonify({'error': 'Subject name is required'}), 400
        
        success = Subject.create_subject(name, description, current_user['id'], year, code)
        
        if success:
            return jsonify({'message': 'Subject created successfully'}), 201
        else:
            return jsonify({'error': 'Subject creation failed'}), 500
            
    except Exception as e:
        return jsonify({'error': f'Failed to create subject: {str(e)}'}), 500

@admin_api.route('/subjects/<int:subject_id>', methods=['PUT'])
@require_admin
def update_subject(current_user, subject_id):
    """Update subject"""
    try:
        data = request.get_json()
        name = data.get('name', '').strip()
        description = data.get('description', '').strip()
        
        if not name:
            return jsonify({'error': 'Subject name is required'}), 400
        
        success = Subject.update_subject(subject_id, name, description)
        
        if success:
            return jsonify({'message': 'Subject updated successfully'}), 200
        else:
            return jsonify({'error': 'Subject update failed'}), 500
            
    except Exception as e:
        return jsonify({'error': f'Failed to update subject: {str(e)}'}), 500

@admin_api.route('/subjects/<int:subject_id>', methods=['DELETE'])
@require_admin
def remove_subject(current_user, subject_id):
    """Remove subject"""
    try:
        success = Subject.delete_subject(subject_id)
        
        if success:
            return jsonify({'message': 'Subject deleted successfully'}), 200
        else:
            return jsonify({'error': 'Subject deletion failed'}), 500
            
    except Exception as e:
        return jsonify({'error': f'Failed to remove subject: {str(e)}'}), 500

# Teacher Invitation Endpoints

@admin_api.route('/subjects/<int:subject_id>/invite-teacher', methods=['POST'])
@require_admin
def invite_teacher(current_user, subject_id):
    """Invite teacher to manage subject"""
    try:
        data = request.get_json()
        teacher_id = data.get('teacher_id')
        
        if not teacher_id:
            return jsonify({'error': 'Teacher ID is required'}), 400
        
        # Check if teacher exists
        teacher = User.get_user_by_id(teacher_id)
        if not teacher or teacher['role'] != 'teacher':
            return jsonify({'error': 'Teacher not found'}), 404
        
        # Check if subject exists
        subject = Subject.get_subject_by_id(subject_id)
        if not subject:
            return jsonify({'error': 'Subject not found'}), 404
        
        # Send invitation
        success, message = SubjectTeacher.invite_teacher(teacher_id, subject_id)
        
        if success:
            # Create notification for teacher
            Notification.create_notification(
                teacher_id,
                'Subject Invitation',
                f'You have been invited to manage the subject "{subject["name"]}".',
                'info'
            )
            
            return jsonify({'message': message}), 201
        else:
            return jsonify({'error': message}), 400
            
    except Exception as e:
        return jsonify({'error': f'Failed to invite teacher: {str(e)}'}), 500

@admin_api.route('/invitations', methods=['GET'])
@require_admin
def list_invitations(current_user):
    """View sent invitations"""
    try:
        invitations = SubjectTeacher.get_all_invitations()
        return jsonify({'invitations': invitations}), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to list invitations: {str(e)}'}), 500

# Student Weakness Tracking Endpoints

@admin_api.route('/students/<int:student_id>/weakness', methods=['GET'])
@require_admin
def get_student_weakness(current_user, student_id):
    """View a student's weak areas"""
    try:
        # Check if student exists
        student = User.get_user_by_id(student_id)
        if not student or student['role'] != 'student':
            return jsonify({'error': 'Student not found'}), 404
        
        # Get student weaknesses
        weaknesses = Weakness.get_student_weaknesses(student_id)
        statistics = Weakness.get_weakness_statistics(student_id)
        
        return jsonify({
            'student': {
                'id': student['id'],
                'username': student['username'],
                'full_name': student.get('full_name')
            },
            'weaknesses': weaknesses,
            'statistics': statistics
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get student weaknesses: {str(e)}'}), 500

# Notification Endpoints

@admin_api.route('/notifications', methods=['GET'])
@require_admin
def list_notifications(current_user):
    """View notifications"""
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        
        notifications = Notification.get_user_notifications(
            current_user['id'], 
            per_page, 
            (page - 1) * per_page
        )
        
        unread_count = Notification.get_unread_count(current_user['id'])
        
        return jsonify({
            'notifications': notifications,
            'unread_count': unread_count,
            'page': page,
            'per_page': per_page
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to list notifications: {str(e)}'}), 500

