"""
Profile Management Controller for AgriQuest

This module handles profile management functionality for all user types.
It provides comprehensive profile management including viewing, editing,
password changes, avatar uploads, and notification management.

Routes:
    /profile/view - View user profile
    /profile/edit - Edit user profile
    /profile/change_password - Change user password
    /profile/upload_avatar - Upload profile picture
    /profile/notifications - Manage notifications

Features:
    - Profile viewing and editing
    - Secure password change with verification
    - Profile picture upload with validation
    - Notification management
    - File upload security and validation

Author: AgriQuest Development Team
Version: 2.0
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from functools import wraps
from werkzeug.utils import secure_filename
import os
from ..models.user import User
from ..models.notification import Notification

profile_bp = Blueprint('profile', __name__, url_prefix='/profile')

def login_required(f):
    """Decorator to require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_id'):
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@profile_bp.route('/view')
@login_required
def view_profile():
    """View user profile"""
    try:
        user_id = session['user_id']
        user = User.get_user_by_id(user_id)
        
        if not user:
            flash('User not found.', 'error')
            return redirect(url_for('quiz.home'))
        
        return render_template('profile_view_profile.html', user=user)
    except Exception as e:
        flash(f'Error loading profile: {e}', 'error')
        return redirect(url_for('quiz.home'))

@profile_bp.route('/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """Edit user profile"""
    try:
        user_id = session['user_id']
        user = User.get_user_by_id(user_id)
        
        if not user:
            flash('User not found.', 'error')
            return redirect(url_for('quiz.home'))
        
        if request.method == 'POST':
            full_name = request.form.get('full_name', '').strip()
            email = request.form.get('email', '').strip()
            
            # Update profile
            success = User.update_profile(user_id, full_name=full_name, email=email)
            
            if success:
                flash('Profile updated successfully!', 'success')
                return redirect(url_for('profile.view_profile'))
            else:
                flash('Failed to update profile.', 'error')
        
        return render_template('profile_edit_profile.html', user=user)
    except Exception as e:
        flash(f'Error editing profile: {e}', 'error')
        return redirect(url_for('profile.view_profile'))

@profile_bp.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change user password"""
    try:
        user_id = session['user_id']
        user = User.get_user_by_id(user_id)
        
        if not user:
            flash('User not found.', 'error')
            return redirect(url_for('quiz.home'))
        
        if request.method == 'POST':
            current_password = request.form.get('current_password', '').strip()
            new_password = request.form.get('new_password', '').strip()
            confirm_password = request.form.get('confirm_password', '').strip()
            
            if not current_password or not new_password or not confirm_password:
                flash('All fields are required.', 'error')
                return render_template('profile_change_password.html', user=user)
            
            if new_password != confirm_password:
                flash('New passwords do not match.', 'error')
                return render_template('profile_change_password.html', user=user)
            
            if len(new_password) < 6:
                flash('New password must be at least 6 characters long.', 'error')
                return render_template('profile_change_password.html', user=user)
            
            success, message = User.change_password(user_id, current_password, new_password)
            
            if success:
                flash(message, 'success')
                return redirect(url_for('profile.view_profile'))
            else:
                flash(message, 'error')
        
        return render_template('profile_change_password.html', user=user)
    except Exception as e:
        flash(f'Error changing password: {e}', 'error')
        return redirect(url_for('profile.view_profile'))

@profile_bp.route('/upload_avatar', methods=['POST'])
@login_required
def upload_avatar():
    """Upload profile picture"""
    try:
        user_id = session['user_id']
        
        if 'profile_picture' not in request.files:
            return jsonify({'success': False, 'error': 'No file selected'})
        
        file = request.files['profile_picture']
        
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'})
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Create unique filename
            import uuid
            unique_filename = f"user_{user_id}_{uuid.uuid4().hex[:12]}.{filename.rsplit('.', 1)[1].lower()}"
            
            # Create uploads directory if it doesn't exist
            upload_dir = 'frontend/static/uploads/profile_pictures'
            os.makedirs(upload_dir, exist_ok=True)
            
            file_path = os.path.join(upload_dir, unique_filename)
            file.save(file_path)
            
            # Update user profile with new picture path
            relative_path = f"static/uploads/profile_pictures/{unique_filename}"
            User.update_profile(user_id, profile_picture=relative_path)
            
            return jsonify({'success': True, 'file_path': relative_path})
        else:
            return jsonify({'success': False, 'error': 'Invalid file type'})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

def allowed_file(filename):
    """Check if file extension is allowed"""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@profile_bp.route('/notifications')
@login_required
def notifications():
    """View user notifications"""
    try:
        user_id = session['user_id']
        notifications = Notification.get_user_notifications(user_id)
        
        return render_template('profile_notifications.html', notifications=notifications)
    except Exception as e:
        flash(f'Error loading notifications: {e}', 'error')
        return redirect(url_for('profile.view_profile'))

@profile_bp.route('/notifications/<int:notification_id>/read', methods=['POST'])
@login_required
def mark_notification_read(notification_id):
    """Mark notification as read"""
    try:
        user_id = session['user_id']
        success = Notification.mark_as_read(notification_id, user_id)
        
        if success:
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Notification not found'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@profile_bp.route('/notifications/mark_all_read', methods=['POST'])
@login_required
def mark_all_notifications_read():
    """Mark all notifications as read"""
    try:
        user_id = session['user_id']
        count = Notification.mark_all_as_read(user_id)
        
        return jsonify({'success': True, 'count': count})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@profile_bp.route('/notifications/<int:notification_id>/delete', methods=['POST'])
@login_required
def delete_notification(notification_id):
    """Delete a notification"""
    try:
        user_id = session['user_id']
        success = Notification.delete_notification(notification_id, user_id)
        
        if success:
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Notification not found'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
