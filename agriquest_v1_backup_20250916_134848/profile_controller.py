"""
Profile Controller
Handles user profile management and display
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from ..models.user import User
from functools import wraps
import os
import uuid
from werkzeug.utils import secure_filename
from PIL import Image

profile_bp = Blueprint('profile', __name__)

# Configuration for file uploads
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
UPLOAD_FOLDER = 'frontend/static/uploads/profile_pictures'

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_profile_picture(file, user_id):
    """Save and process profile picture"""
    if not file or not allowed_file(file.filename):
        return None
    
    # Generate unique filename
    file_extension = file.filename.rsplit('.', 1)[1].lower()
    filename = f"user_{user_id}_{uuid.uuid4().hex}.{file_extension}"
    
    # Ensure upload directory exists
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    # Full path for saving
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    
    try:
        # Open and process image
        with Image.open(file) as img:
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            
            # Resize to 300x300 while maintaining aspect ratio
            img.thumbnail((300, 300), Image.Resampling.LANCZOS)
            
            # Create a square image with white background
            square_img = Image.new('RGB', (300, 300), (255, 255, 255))
            
            # Calculate position to center the image
            x = (300 - img.width) // 2
            y = (300 - img.height) // 2
            square_img.paste(img, (x, y))
            
            # Save the processed image
            square_img.save(file_path, 'JPEG', quality=85)
        
        # Return relative path for database storage
        return f"uploads/profile_pictures/{filename}"
        
    except Exception as e:
        print(f"Error processing image: {e}")
        return None

def delete_old_profile_picture(user_id):
    """Delete old profile picture file"""
    try:
        old_path = User.get_profile_picture_path(user_id)
        if old_path and old_path.startswith('uploads/'):
            full_path = os.path.join('frontend/static', old_path)
            if os.path.exists(full_path):
                os.remove(full_path)
                print(f"Deleted old profile picture: {full_path}")
    except Exception as e:
        print(f"Error deleting old profile picture: {e}")

@profile_bp.route('/profile')
@login_required
def view_profile():
    """View user profile"""
    user_id = session['user_id']
    role = session['role']
    
    # Get user information
    user = User.get_user_by_id(user_id)
    if not user:
        flash('User not found.', 'error')
        return redirect(url_for('auth.login'))
    
    # Get recent activities
    activities = User.get_recent_activities(user_id, role)
    
    if role == 'student':
        # Get student performance
        performance = User.get_user_performance(user_id)
        return render_template('student_profile.html', 
                             user=user, 
                             performance=performance, 
                             activities=activities)
    else:
        # Get teacher's quizzes
        quizzes = User.get_teacher_quizzes(user_id)
        return render_template('teacher_profile.html', 
                             user=user, 
                             quizzes=quizzes, 
                             activities=activities)

@profile_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """Edit user profile"""
    user_id = session['user_id']
    
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip()
        
        # Validate inputs
        if not full_name:
            flash('Full name is required.', 'error')
            return redirect(url_for('profile.edit_profile'))
        
        # Handle profile picture upload
        profile_picture_path = None
        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file and file.filename != '':
                # Check file size
                file.seek(0, 2)  # Seek to end
                file_size = file.tell()
                file.seek(0)  # Reset to beginning
                
                if file_size > MAX_FILE_SIZE:
                    flash('File size too large. Maximum size is 5MB.', 'error')
                    return redirect(url_for('profile.edit_profile'))
                
                # Delete old profile picture
                delete_old_profile_picture(user_id)
                
                # Save new profile picture
                profile_picture_path = save_profile_picture(file, user_id)
                if not profile_picture_path:
                    flash('Invalid file type. Please upload a valid image (PNG, JPG, JPEG, GIF, or WebP).', 'error')
                    return redirect(url_for('profile.edit_profile'))
        
        # Update profile
        success = User.update_profile(user_id, full_name=full_name, email=email, profile_picture=profile_picture_path)
        
        if success:
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('profile.view_profile'))
        else:
            flash('Failed to update profile. Please try again.', 'error')
            return redirect(url_for('profile.edit_profile'))
    
    # Get current user information
    user = User.get_user_by_id(user_id)
    if not user:
        flash('User not found.', 'error')
        return redirect(url_for('auth.login'))
    
    return render_template('edit_profile.html', user=user)

@profile_bp.route('/profile/delete_picture', methods=['POST'])
@login_required
def delete_profile_picture():
    """Delete user's profile picture"""
    user_id = session['user_id']
    
    # Delete old profile picture file
    delete_old_profile_picture(user_id)
    
    # Remove from database
    success = User.delete_profile_picture(user_id)
    
    if success:
        flash('Profile picture deleted successfully!', 'success')
    else:
        flash('Failed to delete profile picture.', 'error')
    
    return redirect(url_for('profile.edit_profile'))
