"""
Student Controller for AgriQuest

This module handles all student functionality for the role-based system.
It provides learning-focused capabilities for students including subject
enrollment, quiz taking, weakness tracking, and progress monitoring.

Routes:
    /student/dashboard - Main student dashboard
    /student/subjects - Browse and enroll in subjects
    /student/my_subjects - View enrolled subjects
    /student/weaknesses - Personal weakness tracking
    /student/search - Search subjects
    /student/notifications - Notification management

Features:
    - Subject enrollment and management
    - Quiz taking for enrolled subjects
    - Personal weakness tracking and analysis
    - Subject search and exploration
    - Enrollment status monitoring
    - Real-time notification system

Author: AgriQuest Development Team
Version: 2.0
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from functools import wraps
from ..models.user import User
from ..models.subject import Subject
from ..models.student_subject import StudentSubject
from ..models.notification import Notification
from ..models.weakness import Weakness
from ..models.quiz import Quiz
from ..models.result import Result

student_bp = Blueprint('student', __name__, url_prefix='/student')

def student_required(f):
    """Decorator to require student role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_id'):
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('auth.login'))
        
        user = User.get_user_by_id(session['user_id'])
        if not user or user['role'] != 'student':
            flash('Access denied. Student privileges required.', 'error')
            return redirect(url_for('quiz.home'))
        
        return f(*args, **kwargs)
    return decorated_function

@student_bp.route('/dashboard')
@student_required
def dashboard():
    """Student dashboard"""
    try:
        student_id = session['user_id']
        
        # Get enrolled subjects
        enrolled_subjects = StudentSubject.get_student_subjects(student_id, 'accepted')
        
        # Get pending requests
        pending_requests = StudentSubject.get_student_subjects(student_id, 'pending')
        
        # Get recent notifications
        recent_notifications = Notification.get_user_notifications(student_id, limit=10)
        
        # Get student's weaknesses
        weaknesses = Weakness.get_student_weaknesses(student_id)
        
        # Get available subjects for enrollment
        all_subjects = Subject.get_all_subjects()
        enrolled_subject_ids = [s['id'] for s in enrolled_subjects]
        available_subjects = [s for s in all_subjects if s['id'] not in enrolled_subject_ids]
        
        # Get recent quiz results
        recent_results = Result.get_user_results(student_id)[:5]
        
        # Get user info for template
        user = User.get_user_by_id(student_id)
        
        return render_template('student_dashboard.html',
                             user=user,
                             enrolled_subjects=enrolled_subjects,
                             pending_requests=pending_requests,
                             recent_notifications=recent_notifications,
                             weaknesses=weaknesses,
                             available_subjects=available_subjects,
                             recent_results=recent_results)
    except Exception as e:
        # Return a simple dashboard with empty data
        user = User.get_user_by_id(session.get('user_id', 0))
        return render_template('student_dashboard.html',
                             user=user,
                             enrolled_subjects=[],
                             pending_requests=[],
                             recent_notifications=[],
                             weaknesses=[],
                             available_subjects=[],
                             recent_results=[])

@student_bp.route('/subjects')
@student_required
def subjects():
    """View all subjects and enrollment status"""
    try:
        student_id = session['user_id']
        
        # Get all subjects
        all_subjects = Subject.get_all_subjects()
        
        # Get student's enrollment status for each subject
        enrolled_subjects = StudentSubject.get_student_subjects(student_id, 'accepted')
        pending_subjects = StudentSubject.get_student_subjects(student_id, 'pending')
        
        enrolled_ids = {s['id'] for s in enrolled_subjects}
        pending_ids = {s['id'] for s in pending_subjects}
        
        # Add enrollment status to each subject
        for subject in all_subjects:
            if subject['id'] in enrolled_ids:
                subject['enrollment_status'] = 'enrolled'
            elif subject['id'] in pending_ids:
                subject['enrollment_status'] = 'pending'
            else:
                subject['enrollment_status'] = 'not_enrolled'
        
        return render_template('student_subjects.html', subjects=all_subjects)
    except Exception as e:
        flash(f'Error loading subjects: {e}', 'error')
        return redirect(url_for('student.dashboard'))

@student_bp.route('/subjects/<int:subject_id>/enroll', methods=['POST'])
@student_required
def enroll_in_subject(subject_id):
    """Request enrollment in a subject"""
    try:
        student_id = session['user_id']
        
        # Check if subject exists
        subject = Subject.get_subject_by_id(subject_id)
        if not subject:
            flash('Subject not found.', 'error')
            return redirect(url_for('student.subjects'))
        
        # Request enrollment
        success, message = StudentSubject.request_enrollment(student_id, subject_id)
        
        if success:
            # Send notification to subject teachers
            from ..models.subject_teacher import SubjectTeacher
            teachers = SubjectTeacher.get_subject_teachers(subject_id, 'accepted')
            student = User.get_user_by_id(student_id)
            
            for teacher in teachers:
                Notification.create_notification(
                    teacher['id'],
                    f"New Enrollment Request: {subject['name']}",
                    f"Student {student['full_name']} ({student['username']}) has requested to enroll in {subject['name']}.",
                    'info'
                )
            
            flash(message, 'success')
        else:
            flash(message, 'error')
        
        return redirect(url_for('student.subjects'))
    except Exception as e:
        flash(f'Error enrolling in subject: {e}', 'error')
        return redirect(url_for('student.subjects'))

@student_bp.route('/subjects/<int:subject_id>/withdraw', methods=['POST'])
@student_required
def withdraw_from_subject(subject_id):
    """Withdraw from a subject"""
    try:
        student_id = session['user_id']
        
        success = StudentSubject.remove_student_from_subject(student_id, subject_id)
        
        if success:
            flash('Successfully withdrew from subject.', 'info')
        else:
            flash('Failed to withdraw from subject.', 'error')
        
        return redirect(url_for('student.subjects'))
    except Exception as e:
        flash(f'Error withdrawing from subject: {e}', 'error')
        return redirect(url_for('student.subjects'))

@student_bp.route('/my_subjects')
@student_required
def my_subjects():
    """View enrolled subjects"""
    try:
        student_id = session['user_id']
        enrolled_subjects = StudentSubject.get_student_subjects(student_id, 'accepted')
        
        return render_template('student_my_subjects.html', subjects=enrolled_subjects)
    except Exception as e:
        flash(f'Error loading enrolled subjects: {e}', 'error')
        return redirect(url_for('student.dashboard'))

@student_bp.route('/subjects/<int:subject_id>/quizzes')
@student_required
def subject_quizzes(subject_id):
    """View quizzes for a subject"""
    try:
        student_id = session['user_id']
        
        # Check if student is enrolled in this subject
        if not StudentSubject.is_enrolled_in_subject(student_id, subject_id):
            flash('You must be enrolled in this subject to view quizzes.', 'error')
            return redirect(url_for('student.subjects'))
        
        subject = Subject.get_subject_by_id(subject_id)
        if not subject:
            flash('Subject not found.', 'error')
            return redirect(url_for('student.my_subjects'))
        
        quizzes = Quiz.get_quizzes_by_subject(subject_id)
        
        return render_template('student_subject_quizzes.html', 
                             subject=subject, 
                             quizzes=quizzes)
    except Exception as e:
        flash(f'Error loading quizzes: {e}', 'error')
        return redirect(url_for('student.my_subjects'))

@student_bp.route('/weaknesses')
@student_required
def my_weaknesses():
    """View student's weaknesses"""
    try:
        student_id = session['user_id']
        subject_id = request.args.get('subject_id', type=int)
        
        if subject_id:
            weaknesses = Weakness.get_student_weaknesses(student_id, subject_id)
            subject = Subject.get_subject_by_id(subject_id)
        else:
            weaknesses = Weakness.get_student_weaknesses(student_id)
            subject = None
        
        # Get enrolled subjects for filter
        enrolled_subjects = StudentSubject.get_student_subjects(student_id, 'accepted')
        
        return render_template('student_weaknesses.html',
                             weaknesses=weaknesses,
                             enrolled_subjects=enrolled_subjects,
                             selected_subject=subject)
    except Exception as e:
        flash(f'Error loading weaknesses: {e}', 'error')
        return redirect(url_for('student.dashboard'))

@student_bp.route('/weaknesses/add', methods=['GET', 'POST'])
@student_required
def add_weakness():
    """Add a weakness"""
    if request.method == 'POST':
        try:
            student_id = session['user_id']
            subject_id = request.form.get('subject_id', type=int)
            weakness_type = request.form.get('weakness_type', '').strip()
            description = request.form.get('description', '').strip()
            
            if not subject_id or not weakness_type:
                flash('Subject and weakness type are required.', 'error')
                return redirect(url_for('student.add_weakness'))
            
            # Check if student is enrolled in this subject
            if not StudentSubject.is_enrolled_in_subject(student_id, subject_id):
                flash('You must be enrolled in this subject to add weaknesses.', 'error')
                return redirect(url_for('student.add_weakness'))
            
            weakness_id = Weakness.add_weakness(student_id, subject_id, weakness_type, description)
            
            if weakness_id:
                flash('Weakness added successfully!', 'success')
                return redirect(url_for('student.my_weaknesses'))
            else:
                flash('Failed to add weakness.', 'error')
        except Exception as e:
            flash(f'Error adding weakness: {e}', 'error')
    
    # Get enrolled subjects
    enrolled_subjects = StudentSubject.get_student_subjects(session['user_id'], 'accepted')
    
    return render_template('student_add_weakness.html', subjects=enrolled_subjects)

@student_bp.route('/weaknesses/<int:weakness_id>/delete', methods=['POST'])
@student_required
def delete_weakness(weakness_id):
    """Delete a weakness"""
    try:
        student_id = session['user_id']
        success = Weakness.delete_weakness(weakness_id, student_id)
        
        if success:
            flash('Weakness deleted successfully.', 'info')
        else:
            flash('Failed to delete weakness.', 'error')
        
        return redirect(url_for('student.my_weaknesses'))
    except Exception as e:
        flash(f'Error deleting weakness: {e}', 'error')
        return redirect(url_for('student.my_weaknesses'))

@student_bp.route('/search')
@student_required
def search_subjects():
    """Search for subjects"""
    try:
        query = request.args.get('q', '').strip()
        
        if not query:
            return render_template('student_search.html', results=[], query=query)
        
        # Search subjects by name or description
        all_subjects = Subject.get_all_subjects()
        results = [s for s in all_subjects if query.lower() in s['name'].lower() or 
                  (s['description'] and query.lower() in s['description'].lower())]
        
        return render_template('student_search.html', results=results, query=query)
    except Exception as e:
        flash(f'Error searching subjects: {e}', 'error')
        return redirect(url_for('student.dashboard'))

@student_bp.route('/notifications')
@student_required
def notifications():
    """View notifications"""
    try:
        notifications = Notification.get_user_notifications(session['user_id'])
        return render_template('student_notifications.html', notifications=notifications)
    except Exception as e:
        flash(f'Error loading notifications: {e}', 'error')
        return redirect(url_for('student.dashboard'))

@student_bp.route('/notifications/<int:notification_id>/read', methods=['POST'])
@student_required
def mark_notification_read(notification_id):
    """Mark notification as read"""
    try:
        Notification.mark_as_read(notification_id, session['user_id'])
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@student_bp.route('/notifications/mark_all_read', methods=['POST'])
@student_required
def mark_all_notifications_read():
    """Mark all notifications as read"""
    try:
        count = Notification.mark_all_as_read(session['user_id'])
        return jsonify({'success': True, 'count': count})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
