"""
Teacher API for AgriQuest v2.0

This module provides REST API endpoints for teacher functionality including
subject management, quiz management, student monitoring, and notifications.

Endpoints:
    GET /api/teacher/subjects - List assigned subjects
    POST /api/teacher/subjects/:id/accept - Accept invitation
    GET /api/teacher/subjects/:id/students - View students in subject
    POST /api/teacher/subjects/:id/students/:studentId/approve - Approve student
    DELETE /api/teacher/subjects/:id/students/:studentId - Remove student
    POST /api/teacher/subjects/:id/quizzes - Create quiz
    GET /api/teacher/subjects/:id/quizzes - View quizzes
    PUT /api/teacher/quizzes/:id - Update quiz
    DELETE /api/teacher/quizzes/:id - Delete quiz
    GET /api/teacher/subjects/:id/weakest-students - View weakest students
    GET /api/teacher/students/search - Search students
    GET /api/teacher/notifications - View notifications

Author: AgriQuest Development Team
Version: 2.0
"""

from flask import Blueprint, request, jsonify
from ..models.subject import Subject
from ..models.subject_teacher import SubjectTeacher
from ..models.student_subject import StudentSubject
from ..models.quiz import Quiz
from ..models.weakness import Weakness
from ..models.notification import Notification
from ..models.user import User
from ..middleware.rbac import require_teacher, can_manage_subject
from datetime import datetime

teacher_api = Blueprint('teacher_api', __name__, url_prefix='/api/teacher')

# Subject Management Endpoints

@teacher_api.route('/subjects', methods=['GET'])
@require_teacher
def list_subjects(current_user):
    """List subjects teacher is assigned to"""
    try:
        subjects = SubjectTeacher.get_teacher_subjects(current_user['id'])
        return jsonify({'subjects': subjects}), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to list subjects: {str(e)}'}), 500

@teacher_api.route('/subjects/<int:subject_id>/accept', methods=['POST'])
@require_teacher
def accept_invitation(current_user, subject_id):
    """Accept admin invitation to manage subject"""
    try:
        success, message = SubjectTeacher.accept_invitation(current_user['id'], subject_id)
        
        if success:
            # Get subject details for notification
            subject = Subject.get_subject_by_id(subject_id)
            if subject:
                # Notify admin
                admin_users = User.get_users_by_role('admin')
                for admin in admin_users:
                    Notification.create_notification(
                        admin['id'],
                        'Invitation Accepted',
                        f'{current_user["full_name"]} accepted the invitation to manage "{subject["name"]}".',
                        'success'
                    )
            
            return jsonify({'message': message}), 200
        else:
            return jsonify({'error': message}), 400
            
    except Exception as e:
        return jsonify({'error': f'Failed to accept invitation: {str(e)}'}), 500

@teacher_api.route('/subjects/<int:subject_id>/students', methods=['GET'])
@require_teacher
def list_subject_students(current_user, subject_id):
    """View students in subject"""
    try:
        # Check if teacher can manage this subject
        if not can_manage_subject(current_user, subject_id):
            return jsonify({'error': 'Access denied'}), 403
        
        students = StudentSubject.get_subject_students(subject_id)
        return jsonify({'students': students}), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to list students: {str(e)}'}), 500

@teacher_api.route('/subjects/<int:subject_id>/students/<int:student_id>/approve', methods=['POST'])
@require_teacher
def approve_student(current_user, subject_id, student_id):
    """Approve student request to join subject"""
    try:
        # Check if teacher can manage this subject
        if not can_manage_subject(current_user, subject_id):
            return jsonify({'error': 'Access denied'}), 403
        
        success, message = StudentSubject.approve_enrollment(student_id, subject_id)
        
        if success:
            # Notify student
            Notification.create_notification(
                student_id,
                'Enrollment Approved',
                f'Your request to join the subject has been approved.',
                'success'
            )
            
            return jsonify({'message': message}), 200
        else:
            return jsonify({'error': message}), 400
            
    except Exception as e:
        return jsonify({'error': f'Failed to approve student: {str(e)}'}), 500

@teacher_api.route('/subjects/<int:subject_id>/students/<int:student_id>', methods=['DELETE'])
@require_teacher
def remove_student(current_user, subject_id, student_id):
    """Remove student from subject"""
    try:
        # Check if teacher can manage this subject
        if not can_manage_subject(current_user, subject_id):
            return jsonify({'error': 'Access denied'}), 403
        
        success = StudentSubject.remove_student(student_id, subject_id)
        
        if success:
            # Notify student
            Notification.create_notification(
                student_id,
                'Removed from Subject',
                f'You have been removed from the subject.',
                'warning'
            )
            
            return jsonify({'message': 'Student removed successfully'}), 200
        else:
            return jsonify({'error': 'Failed to remove student'}), 500
            
    except Exception as e:
        return jsonify({'error': f'Failed to remove student: {str(e)}'}), 500

# Quiz Management Endpoints

@teacher_api.route('/subjects/<int:subject_id>/quizzes', methods=['POST'])
@require_teacher
def create_quiz(current_user, subject_id):
    """Create quiz for subject"""
    try:
        # Check if teacher can manage this subject
        if not can_manage_subject(current_user, subject_id):
            return jsonify({'error': 'Access denied'}), 403
        
        data = request.get_json()
        title = data.get('title', '').strip()
        description = data.get('description', '').strip()
        difficulty_level = data.get('difficulty_level', 'beginner')
        time_limit = data.get('time_limit', 0)
        deadline = data.get('deadline')
        
        if not title:
            return jsonify({'error': 'Quiz title is required'}), 400
        
        # Validate difficulty level
        if difficulty_level not in ['beginner', 'intermediate', 'advanced']:
            return jsonify({'error': 'Invalid difficulty level'}), 400
        
        # Parse deadline if provided
        deadline_datetime = None
        if deadline:
            try:
                deadline_datetime = datetime.fromisoformat(deadline.replace('Z', '+00:00'))
            except ValueError:
                return jsonify({'error': 'Invalid deadline format'}), 400
        
        success = Quiz.create_quiz(
            title=title,
            subject_id=subject_id,
            creator_id=current_user['id'],
            description=description,
            difficulty_level=difficulty_level,
            time_limit=time_limit,
            deadline=deadline_datetime
        )
        
        if success:
            # Notify enrolled students
            students = StudentSubject.get_subject_students(subject_id)
            for student in students:
                if student['status'] == 'approved':
                    Notification.create_notification(
                        student['id'],
                        'New Quiz Available',
                        f'A new quiz "{title}" is now available.',
                        'info'
                    )
            
            return jsonify({'message': 'Quiz created successfully'}), 201
        else:
            return jsonify({'error': 'Quiz creation failed'}), 500
            
    except Exception as e:
        return jsonify({'error': f'Failed to create quiz: {str(e)}'}), 500

@teacher_api.route('/subjects/<int:subject_id>/quizzes', methods=['GET'])
@require_teacher
def list_subject_quizzes(current_user, subject_id):
    """View quizzes in subject"""
    try:
        # Check if teacher can manage this subject
        if not can_manage_subject(current_user, subject_id):
            return jsonify({'error': 'Access denied'}), 403
        
        quizzes = Quiz.get_quizzes_by_subject(subject_id)
        return jsonify({'quizzes': quizzes}), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to list quizzes: {str(e)}'}), 500

@teacher_api.route('/quizzes/<int:quiz_id>', methods=['PUT'])
@require_teacher
def update_quiz(current_user, quiz_id):
    """Update quiz"""
    try:
        # Get quiz to check ownership
        quiz = Quiz.get_quiz_by_id(quiz_id)
        if not quiz:
            return jsonify({'error': 'Quiz not found'}), 404
        
        if quiz['creator_id'] != current_user['id']:
            return jsonify({'error': 'Access denied'}), 403
        
        data = request.get_json()
        title = data.get('title', '').strip()
        description = data.get('description', '').strip()
        difficulty_level = data.get('difficulty_level', 'beginner')
        time_limit = data.get('time_limit', 0)
        deadline = data.get('deadline')
        
        if not title:
            return jsonify({'error': 'Quiz title is required'}), 400
        
        # Parse deadline if provided
        deadline_datetime = None
        if deadline:
            try:
                deadline_datetime = datetime.fromisoformat(deadline.replace('Z', '+00:00'))
            except ValueError:
                return jsonify({'error': 'Invalid deadline format'}), 400
        
        success = Quiz.update_quiz(
            quiz_id=quiz_id,
            title=title,
            description=description,
            difficulty_level=difficulty_level,
            time_limit=time_limit,
            deadline=deadline_datetime
        )
        
        if success:
            return jsonify({'message': 'Quiz updated successfully'}), 200
        else:
            return jsonify({'error': 'Quiz update failed'}), 500
            
    except Exception as e:
        return jsonify({'error': f'Failed to update quiz: {str(e)}'}), 500

@teacher_api.route('/quizzes/<int:quiz_id>', methods=['DELETE'])
@require_teacher
def delete_quiz(current_user, quiz_id):
    """Delete quiz"""
    try:
        # Get quiz to check ownership
        quiz = Quiz.get_quiz_by_id(quiz_id)
        if not quiz:
            return jsonify({'error': 'Quiz not found'}), 404
        
        if quiz['creator_id'] != current_user['id']:
            return jsonify({'error': 'Access denied'}), 403
        
        success = Quiz.delete_quiz(quiz_id)
        
        if success:
            return jsonify({'message': 'Quiz deleted successfully'}), 200
        else:
            return jsonify({'error': 'Quiz deletion failed'}), 500
            
    except Exception as e:
        return jsonify({'error': f'Failed to delete quiz: {str(e)}'}), 500

# Student Monitoring Endpoints

@teacher_api.route('/subjects/<int:subject_id>/weakest-students', methods=['GET'])
@require_teacher
def get_weakest_students(current_user, subject_id):
    """View weakest students in subject"""
    try:
        # Check if teacher can manage this subject
        if not can_manage_subject(current_user, subject_id):
            return jsonify({'error': 'Access denied'}), 403
        
        limit = int(request.args.get('limit', 10))
        students = Weakness.get_weakest_students(subject_id, limit)
        
        return jsonify({'students': students}), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get weakest students: {str(e)}'}), 500

@teacher_api.route('/students/search', methods=['GET'])
@require_teacher
def search_students(current_user):
    """Search for students"""
    try:
        query = request.args.get('query', '').strip()
        
        if not query:
            return jsonify({'error': 'Search query is required'}), 400
        
        students = User.search_users(query, 'student')
        
        return jsonify({
            'students': students,
            'total': len(students)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to search students: {str(e)}'}), 500

# Notification Endpoints

@teacher_api.route('/notifications', methods=['GET'])
@require_teacher
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

# Pending Requests Endpoint

@teacher_api.route('/pending-requests', methods=['GET'])
@require_teacher
def list_pending_requests(current_user):
    """View pending enrollment requests"""
    try:
        requests = StudentSubject.get_pending_requests(current_user['id'])
        return jsonify({'requests': requests}), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to list pending requests: {str(e)}'}), 500

