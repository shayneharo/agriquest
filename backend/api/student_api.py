"""
Student API for AgriQuest v2.0

This module provides REST API endpoints for student functionality including
enrollment, quiz taking, weakness tracking, and notifications.

Endpoints:
    GET /api/student/subjects - List enrolled subjects
    GET /api/student/subjects/search - Search available subjects
    POST /api/student/subjects/:id/request - Request to join subject
    DELETE /api/student/subjects/:id/leave - Leave subject
    GET /api/student/subjects/:id/quizzes - List quizzes (if enrolled)
    POST /api/student/quizzes/:id/submit - Submit quiz answers
    GET /api/student/quizzes/:id/result - View quiz result
    GET /api/student/weakness - View personal weak areas
    GET /api/student/notifications - View notifications

Author: AgriQuest Development Team
Version: 2.0
"""

from flask import Blueprint, request, jsonify
from ..models.subject import Subject
from ..models.student_subject import StudentSubject
from ..models.quiz import Quiz
from ..models.result import Result
from ..models.weakness import Weakness
from ..models.notification import Notification
from ..middleware.rbac import require_student, can_access_subject
from datetime import datetime

student_api = Blueprint('student_api', __name__, url_prefix='/api/student')

# Enrollment Endpoints

@student_api.route('/subjects', methods=['GET'])
@require_student
def list_enrolled_subjects(current_user):
    """List enrolled subjects"""
    try:
        subjects = StudentSubject.get_student_subjects(current_user['id'])
        return jsonify({'subjects': subjects}), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to list subjects: {str(e)}'}), 500

@student_api.route('/subjects/search', methods=['GET'])
@require_student
def search_subjects(current_user):
    """Search for available subjects"""
    try:
        query = request.args.get('query', '').strip()
        
        if not query:
            return jsonify({'error': 'Search query is required'}), 400
        
        # Get all subjects
        all_subjects = Subject.get_all_subjects()
        
        # Filter by search query
        filtered_subjects = [
            subject for subject in all_subjects
            if query.lower() in subject['name'].lower() or 
               query.lower() in subject.get('description', '').lower()
        ]
        
        # Check enrollment status for each subject
        enrolled_subject_ids = {
            subject['id'] for subject in StudentSubject.get_student_subjects(current_user['id'])
        }
        
        for subject in filtered_subjects:
            subject['is_enrolled'] = subject['id'] in enrolled_subject_ids
        
        return jsonify({
            'subjects': filtered_subjects,
            'total': len(filtered_subjects)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to search subjects: {str(e)}'}), 500

@student_api.route('/subjects/<int:subject_id>/request', methods=['POST'])
@require_student
def request_enrollment(current_user, subject_id):
    """Request to join subject"""
    try:
        # Check if subject exists
        subject = Subject.get_subject_by_id(subject_id)
        if not subject:
            return jsonify({'error': 'Subject not found'}), 404
        
        # Check if already enrolled
        if StudentSubject.is_student_enrolled(current_user['id'], subject_id):
            return jsonify({'error': 'Already enrolled in this subject'}), 400
        
        success, message = StudentSubject.request_enrollment(current_user['id'], subject_id)
        
        if success:
            # Notify teachers who manage this subject
            from ..models.subject_teacher import SubjectTeacher
            teachers = SubjectTeacher.get_subject_teachers(subject_id)
            for teacher in teachers:
                if teacher['status'] == 'accepted':
                    Notification.create_notification(
                        teacher['id'],
                        'Enrollment Request',
                        f'{current_user["full_name"]} wants to join "{subject["name"]}".',
                        'info'
                    )
            
            return jsonify({'message': message}), 201
        else:
            return jsonify({'error': message}), 400
            
    except Exception as e:
        return jsonify({'error': f'Failed to request enrollment: {str(e)}'}), 500

@student_api.route('/subjects/<int:subject_id>/leave', methods=['DELETE'])
@require_student
def leave_subject(current_user, subject_id):
    """Leave subject"""
    try:
        success = StudentSubject.remove_student(current_user['id'], subject_id)
        
        if success:
            return jsonify({'message': 'Left subject successfully'}), 200
        else:
            return jsonify({'error': 'Failed to leave subject'}), 500
            
    except Exception as e:
        return jsonify({'error': f'Failed to leave subject: {str(e)}'}), 500

# Quiz Endpoints

@student_api.route('/subjects/<int:subject_id>/quizzes', methods=['GET'])
@require_student
def list_subject_quizzes(current_user, subject_id):
    """List quizzes (only if enrolled)"""
    try:
        # Check if student is enrolled
        if not can_access_subject(current_user, subject_id):
            return jsonify({'error': 'Access denied. You must be enrolled in this subject.'}), 403
        
        quizzes = Quiz.get_quizzes_by_subject(subject_id)
        
        # Add enrollment status and check if quiz is open
        for quiz in quizzes:
            quiz['is_open'] = Quiz.is_quiz_open(quiz['id'])
        
        return jsonify({'quizzes': quizzes}), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to list quizzes: {str(e)}'}), 500

@student_api.route('/quizzes/<int:quiz_id>/submit', methods=['POST'])
@require_student
def submit_quiz(current_user, quiz_id):
    """Submit quiz answers"""
    try:
        # Get quiz details
        quiz = Quiz.get_quiz_by_id(quiz_id)
        if not quiz:
            return jsonify({'error': 'Quiz not found'}), 404
        
        # Check if student is enrolled in the subject
        if not can_access_subject(current_user, quiz['subject_id']):
            return jsonify({'error': 'Access denied. You must be enrolled in this subject.'}), 403
        
        # Check if quiz is still open
        if not Quiz.is_quiz_open(quiz_id):
            return jsonify({'error': 'Quiz is closed'}), 400
        
        data = request.get_json()
        answers = data.get('answers', [])
        
        if not answers:
            return jsonify({'error': 'Answers are required'}), 400
        
        # Get quiz questions
        questions = Quiz.get_quiz_questions(quiz_id)
        if not questions:
            return jsonify({'error': 'No questions found for this quiz'}), 400
        
        # Calculate score
        correct_answers = 0
        total_questions = len(questions)
        
        for i, question in enumerate(questions):
            if i < len(answers) and answers[i] == question['correct_option']:
                correct_answers += 1
        
        # Save result
        success = Result.create_result(
            user_id=current_user['id'],
            quiz_id=quiz_id,
            score=correct_answers,
            total_questions=total_questions
        )
        
        if success:
            # Analyze weaknesses
            percentage = (correct_answers / total_questions) * 100
            if percentage < 60:  # Below 60% is considered weak
                Weakness.add_weakness(
                    user_id=current_user['id'],
                    subject_id=quiz['subject_id'],
                    weakness_type='quiz_performance',
                    description=f'Scored {percentage:.1f}% on quiz "{quiz["title"]}"'
                )
            
            return jsonify({
                'message': 'Quiz submitted successfully',
                'score': correct_answers,
                'total_questions': total_questions,
                'percentage': round(percentage, 1)
            }), 200
        else:
            return jsonify({'error': 'Failed to save quiz result'}), 500
            
    except Exception as e:
        return jsonify({'error': f'Failed to submit quiz: {str(e)}'}), 500

@student_api.route('/quizzes/<int:quiz_id>/result', methods=['GET'])
@require_student
def get_quiz_result(current_user, quiz_id):
    """View quiz result"""
    try:
        # Get quiz details
        quiz = Quiz.get_quiz_by_id(quiz_id)
        if not quiz:
            return jsonify({'error': 'Quiz not found'}), 404
        
        # Check if student is enrolled in the subject
        if not can_access_subject(current_user, quiz['subject_id']):
            return jsonify({'error': 'Access denied. You must be enrolled in this subject.'}), 403
        
        # Get student's result for this quiz
        result = Result.get_user_quiz_result(current_user['id'], quiz_id)
        
        if not result:
            return jsonify({'error': 'No result found for this quiz'}), 404
        
        return jsonify({
            'quiz': {
                'id': quiz['id'],
                'title': quiz['title'],
                'subject_id': quiz['subject_id']
            },
            'result': result
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get quiz result: {str(e)}'}), 500

# Weakness Tracking Endpoints

@student_api.route('/weakness', methods=['GET'])
@require_student
def get_weaknesses(current_user):
    """View personal weak areas"""
    try:
        subject_id = request.args.get('subject_id', type=int)
        
        if subject_id:
            weaknesses = Weakness.get_student_weaknesses(current_user['id'], subject_id)
        else:
            weaknesses = Weakness.get_student_weaknesses(current_user['id'])
        
        statistics = Weakness.get_weakness_statistics(current_user['id'])
        
        return jsonify({
            'weaknesses': weaknesses,
            'statistics': statistics
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get weaknesses: {str(e)}'}), 500

# Notification Endpoints

@student_api.route('/notifications', methods=['GET'])
@require_student
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

# Quiz History Endpoint

@student_api.route('/quiz-history', methods=['GET'])
@require_student
def get_quiz_history(current_user):
    """Get student's quiz history"""
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        
        results = Result.get_user_results(
            current_user['id'], 
            per_page, 
            (page - 1) * per_page
        )
        
        return jsonify({
            'results': results,
            'page': page,
            'per_page': per_page
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get quiz history: {str(e)}'}), 500

