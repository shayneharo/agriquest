"""
Teacher Controller for AgriQuest

This module handles all teacher functionality for the role-based system.
It provides subject-specific management capabilities for teachers including
invitation management, student enrollment approval, and subject oversight.

Routes:
    /teacher/dashboard - Main teacher dashboard
    /teacher/invitations - Manage subject invitations
    /teacher/subjects - View assigned subjects
    /teacher/weaknesses - Student weakness tracking
    /teacher/search - Search students
    /teacher/notifications - Notification management

Features:
    - Accept/reject subject invitations from admin
    - Manage student enrollment requests
    - Create and manage quizzes for assigned subjects
    - Track student performance and weaknesses
    - Search and manage students
    - Real-time notification system

Author: AgriQuest Development Team
Version: 2.0
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from functools import wraps
from ..models.user import User
from ..models.subject import Subject
from ..models.subject_teacher import SubjectTeacher
from ..models.student_subject import StudentSubject
from ..models.notification import Notification
from ..models.weakness import Weakness
from ..models.quiz import Quiz
from ..models.result import Result

teacher_bp = Blueprint('teacher', __name__, url_prefix='/teacher')

def teacher_required(f):
    """Decorator to require teacher role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_id'):
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('auth.login'))
        
        user = User.get_user_by_id(session['user_id'])
        if not user or user['role'] != 'teacher':
            flash('Access denied. Teacher privileges required.', 'error')
            return redirect(url_for('quiz.home'))
        
        return f(*args, **kwargs)
    return decorated_function

@teacher_bp.route('/dashboard')
@teacher_required
def dashboard():
    """Teacher dashboard"""
    try:
        teacher_id = session['user_id']
        
        # Get teacher's subjects
        subjects = SubjectTeacher.get_teacher_subjects(teacher_id, 'accepted')
        
        # Get pending invitations
        pending_invitations = SubjectTeacher.get_pending_invitations(teacher_id)
        
        # Get recent notifications
        recent_notifications = Notification.get_user_notifications(teacher_id, limit=10)
        
        # Get pending student requests for teacher's subjects
        pending_requests = []
        for subject in subjects:
            requests = StudentSubject.get_pending_requests(subject['id'])
            pending_requests.extend(requests)
        
        # Get recent quiz activity
        recent_quizzes = Quiz.get_quizzes_by_creator(teacher_id)[:5]
        
        return render_template('teacher_dashboard.html',
                             subjects=subjects,
                             pending_invitations=pending_invitations,
                             recent_notifications=recent_notifications,
                             pending_requests=pending_requests,
                             recent_quizzes=recent_quizzes)
    except Exception as e:
        # Return a simple dashboard with empty data
        return render_template('teacher_dashboard.html',
                             subjects=[],
                             pending_invitations=[],
                             recent_notifications=[],
                             pending_requests=[],
                             recent_quizzes=[])

@teacher_bp.route('/invitations')
@teacher_required
def invitations():
    """View and manage invitations"""
    try:
        teacher_id = session['user_id']
        invitations = SubjectTeacher.get_pending_invitations(teacher_id)
        
        return render_template('teacher_invitations.html', invitations=invitations)
    except Exception as e:
        flash(f'Error loading invitations: {e}', 'error')
        return redirect(url_for('teacher.dashboard'))

@teacher_bp.route('/invitations/<int:subject_id>/accept', methods=['POST'])
@teacher_required
def accept_invitation(subject_id):
    """Accept a subject invitation"""
    try:
        teacher_id = session['user_id']
        success, message = SubjectTeacher.accept_invitation(teacher_id, subject_id)
        
        if success:
            # Send notification to admin
            subject = Subject.get_subject_by_id(subject_id)
            admin_users = User.get_users_by_role('admin')
            for admin in admin_users:
                Notification.create_notification(
                    admin['id'],
                    f"Invitation Accepted: {subject['name']}",
                    f"Teacher {session.get('username', 'Unknown')} has accepted the invitation to manage {subject['name']}.",
                    'success'
                )
            
            flash(message, 'success')
        else:
            flash(message, 'error')
        
        return redirect(url_for('teacher.invitations'))
    except Exception as e:
        flash(f'Error accepting invitation: {e}', 'error')
        return redirect(url_for('teacher.invitations'))

@teacher_bp.route('/invitations/<int:subject_id>/reject', methods=['POST'])
@teacher_required
def reject_invitation(subject_id):
    """Reject a subject invitation"""
    try:
        teacher_id = session['user_id']
        success, message = SubjectTeacher.reject_invitation(teacher_id, subject_id)
        
        if success:
            flash(message, 'info')
        else:
            flash(message, 'error')
        
        return redirect(url_for('teacher.invitations'))
    except Exception as e:
        flash(f'Error rejecting invitation: {e}', 'error')
        return redirect(url_for('teacher.invitations'))

@teacher_bp.route('/subjects')
@teacher_required
def my_subjects():
    """View teacher's subjects"""
    try:
        teacher_id = session['user_id']
        subjects = SubjectTeacher.get_teacher_subjects(teacher_id, 'accepted')
        
        return render_template('teacher_subjects.html', subjects=subjects)
    except Exception as e:
        flash(f'Error loading subjects: {e}', 'error')
        return redirect(url_for('teacher.dashboard'))

@teacher_bp.route('/subjects/<int:subject_id>')
@teacher_required
def subject_detail(subject_id):
    """View subject details and manage students"""
    try:
        teacher_id = session['user_id']
        
        # Check if teacher is assigned to this subject
        if not SubjectTeacher.is_teacher_of_subject(teacher_id, subject_id):
            flash('You are not assigned to this subject.', 'error')
            return redirect(url_for('teacher.my_subjects'))
        
        subject = Subject.get_subject_by_id(subject_id)
        if not subject:
            flash('Subject not found.', 'error')
            return redirect(url_for('teacher.my_subjects'))
        
        # Get enrolled students
        students = StudentSubject.get_subject_students(subject_id, 'accepted')
        
        # Get pending requests
        pending_requests = StudentSubject.get_pending_requests(subject_id)
        
        # Get subject quizzes
        quizzes = Quiz.get_quizzes_by_subject(subject_id)
        
        return render_template('teacher_subject_detail.html',
                             subject=subject,
                             students=students,
                             pending_requests=pending_requests,
                             quizzes=quizzes)
    except Exception as e:
        flash(f'Error loading subject details: {e}', 'error')
        return redirect(url_for('teacher.my_subjects'))

@teacher_bp.route('/subjects/<int:subject_id>/approve_student/<int:student_id>', methods=['POST'])
@teacher_required
def approve_student(student_id, subject_id):
    """Approve student enrollment request"""
    try:
        teacher_id = session['user_id']
        
        # Check if teacher is assigned to this subject
        if not SubjectTeacher.is_teacher_of_subject(teacher_id, subject_id):
            flash('You are not assigned to this subject.', 'error')
            return redirect(url_for('teacher.subject_detail', subject_id=subject_id))
        
        success, message = StudentSubject.approve_enrollment(student_id, subject_id, teacher_id)
        
        if success:
            # Send notification to student
            student = User.get_user_by_id(student_id)
            subject = Subject.get_subject_by_id(subject_id)
            Notification.create_notification(
                student_id,
                f"Enrollment Approved: {subject['name']}",
                f"Your enrollment request for {subject['name']} has been approved.",
                'success'
            )
            
            flash(message, 'success')
        else:
            flash(message, 'error')
        
        return redirect(url_for('teacher.subject_detail', subject_id=subject_id))
    except Exception as e:
        flash(f'Error approving student: {e}', 'error')
        return redirect(url_for('teacher.subject_detail', subject_id=subject_id))

@teacher_bp.route('/subjects/<int:subject_id>/reject_student/<int:student_id>', methods=['POST'])
@teacher_required
def reject_student(student_id, subject_id):
    """Reject student enrollment request"""
    try:
        teacher_id = session['user_id']
        
        # Check if teacher is assigned to this subject
        if not SubjectTeacher.is_teacher_of_subject(teacher_id, subject_id):
            flash('You are not assigned to this subject.', 'error')
            return redirect(url_for('teacher.subject_detail', subject_id=subject_id))
        
        success, message = StudentSubject.reject_enrollment(student_id, subject_id)
        
        if success:
            # Send notification to student
            student = User.get_user_by_id(student_id)
            subject = Subject.get_subject_by_id(subject_id)
            Notification.create_notification(
                student_id,
                f"Enrollment Rejected: {subject['name']}",
                f"Your enrollment request for {subject['name']} has been rejected.",
                'error'
            )
            
            flash(message, 'info')
        else:
            flash(message, 'error')
        
        return redirect(url_for('teacher.subject_detail', subject_id=subject_id))
    except Exception as e:
        flash(f'Error rejecting student: {e}', 'error')
        return redirect(url_for('teacher.subject_detail', subject_id=subject_id))

@teacher_bp.route('/weaknesses')
@teacher_required
def view_weaknesses():
    """View student weaknesses in teacher's subjects"""
    try:
        teacher_id = session['user_id']
        subject_id = request.args.get('subject_id', type=int)
        
        # Get teacher's subjects
        teacher_subjects = SubjectTeacher.get_teacher_subjects(teacher_id, 'accepted')
        
        if subject_id:
            # Check if teacher is assigned to this subject
            if not SubjectTeacher.is_teacher_of_subject(teacher_id, subject_id):
                flash('You are not assigned to this subject.', 'error')
                return redirect(url_for('teacher.view_weaknesses'))
            
            weaknesses = Weakness.get_subject_weaknesses(subject_id)
            struggling_students = Weakness.get_struggling_students(subject_id)
            subject = Subject.get_subject_by_id(subject_id)
        else:
            weaknesses = []
            struggling_students = []
            subject = None
        
        return render_template('teacher_weaknesses.html',
                             teacher_subjects=teacher_subjects,
                             selected_subject=subject,
                             weaknesses=weaknesses,
                             struggling_students=struggling_students)
    except Exception as e:
        flash(f'Error loading weaknesses: {e}', 'error')
        return redirect(url_for('teacher.dashboard'))

@teacher_bp.route('/search')
@teacher_required
def search_students():
    """Search for students"""
    try:
        query = request.args.get('q', '').strip()
        
        if not query:
            return render_template('teacher_search.html', results=[], query=query)
        
        students = User.search_users(query, 'student')
        
        return render_template('teacher_search.html', results=students, query=query)
    except Exception as e:
        flash(f'Error searching students: {e}', 'error')
        return redirect(url_for('teacher.dashboard'))

@teacher_bp.route('/notifications')
@teacher_required
def notifications():
    """View notifications"""
    try:
        notifications = Notification.get_user_notifications(session['user_id'])
        return render_template('teacher_notifications.html', notifications=notifications)
    except Exception as e:
        flash(f'Error loading notifications: {e}', 'error')
        return redirect(url_for('teacher.dashboard'))

@teacher_bp.route('/notifications/<int:notification_id>/read', methods=['POST'])
@teacher_required
def mark_notification_read(notification_id):
    """Mark notification as read"""
    try:
        Notification.mark_as_read(notification_id, session['user_id'])
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@teacher_bp.route('/notifications/mark_all_read', methods=['POST'])
@teacher_required
def mark_all_notifications_read():
    """Mark all notifications as read"""
    try:
        count = Notification.mark_all_as_read(session['user_id'])
        return jsonify({'success': True, 'count': count})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
