"""
Admin/Adviser Controller for AgriQuest

This module handles all administrative functionality for the role-based system.
It provides comprehensive management capabilities for admins/advisers including
user management, subject management, teacher invitations, and system oversight.

Routes:
    /admin/dashboard - Main admin dashboard
    /admin/subjects - Subject management
    /admin/users - User management
    /admin/weaknesses - Student weakness tracking
    /admin/search - Search functionality
    /admin/notifications - Notification management

Features:
    - Complete user management (add/remove teachers and students)
    - Subject creation and management
    - Teacher invitation system
    - Student weakness analysis
    - System-wide search functionality
    - Real-time notification management

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

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_id'):
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('auth.login'))
        
        user = User.get_user_by_id(session['user_id'])
        if not user or user['role'] != 'admin':
            flash('Access denied. Admin privileges required.', 'error')
            return redirect(url_for('auth.login'))
        
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    """Admin dashboard"""
    try:
        # Get basic statistics with error handling
        total_users = 0
        total_teachers = 0
        total_students = 0
        total_subjects = 0
        recent_notifications = []
        pending_invitations = []
        pending_requests = []
        
        try:
            total_users = len(User.get_all_users())
        except:
            pass
            
        try:
            total_teachers = len(User.get_users_by_role('teacher'))
        except:
            pass
            
        try:
            total_students = len(User.get_users_by_role('student'))
        except:
            pass
            
        try:
            total_subjects = len(Subject.get_all_subjects())
        except:
            pass
        
        # Get recent activity
        try:
            recent_notifications = Notification.get_user_notifications(session['user_id'], limit=10)
        except:
            recent_notifications = []
        
        # Get pending invitations
        try:
            for teacher in User.get_users_by_role('teacher'):
                invitations = SubjectTeacher.get_pending_invitations(teacher['id'])
                pending_invitations.extend(invitations)
        except:
            pending_invitations = []
        
        # Get pending enrollment requests
        try:
            pending_requests = StudentSubject.get_pending_requests()
        except:
            pending_requests = []
        
        return render_template('admin_dashboard.html',
                             total_users=total_users,
                             total_teachers=total_teachers,
                             total_students=total_students,
                             total_subjects=total_subjects,
                             recent_notifications=recent_notifications,
                             pending_invitations=pending_invitations,
                             pending_requests=pending_requests)
    except Exception as e:
        print(f"Admin dashboard error: {e}")
        # Return a simple dashboard instead of redirecting
        return render_template('admin_dashboard.html',
                             total_users=0,
                             total_teachers=0,
                             total_students=0,
                             total_subjects=0,
                             recent_notifications=[],
                             pending_invitations=[],
                             pending_requests=[])

@admin_bp.route('/subjects')
@admin_required
def manage_subjects():
    """Manage subjects"""
    try:
        subjects = Subject.get_all_subjects()
        return render_template('admin_subjects.html', subjects=subjects)
    except Exception as e:
        flash(f'Error loading subjects: {e}', 'error')
        return redirect(url_for('admin.dashboard'))

@admin_bp.route('/subjects/create', methods=['GET', 'POST'])
@admin_required
def create_subject():
    """Create a new subject"""
    if request.method == 'POST':
        try:
            name = request.form.get('name', '').strip()
            description = request.form.get('description', '').strip()
            
            if not name:
                flash('Subject name is required.', 'error')
                return render_template('admin_create_subject.html')
            
            # Create subject
            subject_id = Subject.create_subject(name, description, session['user_id'])
            
            if subject_id:
                flash('Subject created successfully!', 'success')
                return redirect(url_for('admin.manage_subjects'))
            else:
                flash('Failed to create subject. Name may already exist.', 'error')
        except Exception as e:
            flash(f'Error creating subject: {e}', 'error')
    
    return render_template('admin_create_subject.html')

@admin_bp.route('/subjects/<int:subject_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_subject(subject_id):
    """Edit a subject"""
    subject = Subject.get_subject_by_id(subject_id)
    if not subject:
        flash('Subject not found.', 'error')
        return redirect(url_for('admin.manage_subjects'))
    
    if request.method == 'POST':
        try:
            name = request.form.get('name', '').strip()
            description = request.form.get('description', '').strip()
            
            if not name:
                flash('Subject name is required.', 'error')
                return render_template('admin_edit_subject.html', subject=subject)
            
            success = Subject.update_subject(subject_id, name, description)
            
            if success:
                flash('Subject updated successfully!', 'success')
                return redirect(url_for('admin.manage_subjects'))
            else:
                flash('Failed to update subject.', 'error')
        except Exception as e:
            flash(f'Error updating subject: {e}', 'error')
    
    return render_template('admin_edit_subject.html', subject=subject)

@admin_bp.route('/users')
@admin_required
def manage_users():
    """Manage users"""
    try:
        role = request.args.get('role', '')
        search = request.args.get('search', '')
        
        if search:
            users = User.search_users(search, role if role else None)
        elif role:
            users = User.get_users_by_role(role)
        else:
            users = [dict(user) for user in User.get_all_users()]
        
        return render_template('admin_users.html', users=users, current_role=role, search_query=search)
    except Exception as e:
        flash(f'Error loading users: {e}', 'error')
        return redirect(url_for('admin.dashboard'))

@admin_bp.route('/users/create', methods=['GET', 'POST'])
@admin_required
def create_user():
    """Create a new user"""
    if request.method == 'POST':
        try:
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '').strip()
            role = request.form.get('role', 'student')
            email = request.form.get('email', '').strip()
            full_name = request.form.get('full_name', '').strip()
            
            if not username or not password:
                flash('Username and password are required.', 'error')
                return render_template('admin_create_user.html')
            
            success = User.create_user(username, password, role, email, full_name)
            
            if success:
                flash('User created successfully!', 'success')
                return redirect(url_for('admin.manage_users'))
            else:
                flash('Failed to create user. Username may already exist.', 'error')
        except Exception as e:
            flash(f'Error creating user: {e}', 'error')
    
    return render_template('admin_create_user.html')

@admin_bp.route('/users/<int:user_id>/toggle_status', methods=['POST'])
@admin_required
def toggle_user_status(user_id):
    """Toggle user active status"""
    try:
        user = User.get_user_by_id(user_id)
        if not user:
            flash('User not found.', 'error')
            return redirect(url_for('admin.manage_users'))
        
        if user['is_active']:
            User.deactivate_user(user_id)
            flash(f'User {user["username"]} deactivated.', 'info')
        else:
            User.activate_user(user_id)
            flash(f'User {user["username"]} activated.', 'info')
        
        return redirect(url_for('admin.manage_users'))
    except Exception as e:
        flash(f'Error toggling user status: {e}', 'error')
        return redirect(url_for('admin.manage_users'))

@admin_bp.route('/subjects/<int:subject_id>/invite_teacher', methods=['GET', 'POST'])
@admin_required
def invite_teacher(subject_id):
    """Invite a teacher to manage a subject"""
    subject = Subject.get_subject_by_id(subject_id)
    if not subject:
        flash('Subject not found.', 'error')
        return redirect(url_for('admin.manage_subjects'))
    
    if request.method == 'POST':
        try:
            teacher_id = request.form.get('teacher_id')
            if not teacher_id:
                flash('Please select a teacher.', 'error')
                return redirect(url_for('admin.invite_teacher', subject_id=subject_id))
            
            success, message = SubjectTeacher.invite_teacher(int(teacher_id), subject_id, session['user_id'])
            
            if success:
                # Send notification to teacher
                teacher = User.get_user_by_id(teacher_id)
                Notification.create_notification(
                    teacher_id,
                    f"Subject Invitation: {subject['name']}",
                    f"You have been invited to manage the subject '{subject['name']}'. Please check your invitations.",
                    'invitation'
                )
                
                flash(message, 'success')
            else:
                flash(message, 'error')
            
            return redirect(url_for('admin.manage_subjects'))
        except Exception as e:
            flash(f'Error inviting teacher: {e}', 'error')
    
    # Get available teachers (not already assigned to this subject)
    teachers = User.get_users_by_role('teacher')
    assigned_teachers = [t['id'] for t in SubjectTeacher.get_subject_teachers(subject_id)]
    available_teachers = [t for t in teachers if t['id'] not in assigned_teachers]
    
    return render_template('admin_invite_teacher.html', 
                         subject=subject, 
                         teachers=available_teachers)

@admin_bp.route('/weaknesses')
@admin_required
def view_weaknesses():
    """View student weaknesses"""
    try:
        subject_id = request.args.get('subject_id', type=int)
        search = request.args.get('search', '')
        
        if subject_id:
            weaknesses = Weakness.get_subject_weaknesses(subject_id)
            subject = Subject.get_subject_by_id(subject_id)
        else:
            weaknesses = []
            subject = None
        
        subjects = Subject.get_all_subjects()
        
        return render_template('admin_weaknesses.html', 
                             weaknesses=weaknesses, 
                             subjects=subjects, 
                             selected_subject=subject,
                             search_query=search)
    except Exception as e:
        flash(f'Error loading weaknesses: {e}', 'error')
        return redirect(url_for('admin.dashboard'))

@admin_bp.route('/search')
@admin_required
def search():
    """Search for students and teachers"""
    try:
        query = request.args.get('q', '').strip()
        role = request.args.get('role', '')
        
        if not query:
            return render_template('admin_search.html', results=[], query=query, role=role)
        
        users = User.search_users(query, role if role else None)
        
        return render_template('admin_search.html', 
                             results=users, 
                             query=query, 
                             role=role)
    except Exception as e:
        flash(f'Error searching: {e}', 'error')
        return redirect(url_for('admin.dashboard'))

@admin_bp.route('/notifications')
@admin_required
def notifications():
    """View notifications"""
    try:
        notifications = Notification.get_user_notifications(session['user_id'])
        return render_template('admin_notifications.html', notifications=notifications)
    except Exception as e:
        flash(f'Error loading notifications: {e}', 'error')
        return redirect(url_for('admin.dashboard'))

@admin_bp.route('/notifications/<int:notification_id>/read', methods=['POST'])
@admin_required
def mark_notification_read(notification_id):
    """Mark notification as read"""
    try:
        Notification.mark_as_read(notification_id, session['user_id'])
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@admin_bp.route('/notifications/mark_all_read', methods=['POST'])
@admin_required
def mark_all_notifications_read():
    """Mark all notifications as read"""
    try:
        count = Notification.mark_all_as_read(session['user_id'])
        return jsonify({'success': True, 'count': count})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
