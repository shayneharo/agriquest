"""
Admin Controller
Handles administrative functions and user management
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from ..models.user import User
from ..models.subject import Subject
from ..models.quiz import Quiz
from .auth_controller import login_required

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin_dashboard')
@login_required
def admin_dashboard():
    """Admin dashboard - redirect to main dashboard"""
    if session.get('role') not in ['teacher', 'admin']:
        flash('Access denied', 'error')
        return redirect(url_for('quiz.home'))
    
    return redirect(url_for('quiz.home'))

@admin_bp.route('/manage_subjects', methods=['GET', 'POST'])
@login_required
def manage_subjects():
    if session.get('role') != 'teacher':
        flash('Access denied', 'error')
        return redirect(url_for('quiz.home'))
    
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        if Subject.create_subject(name, description, session['user_id']):
            flash('Subject created successfully!', 'success')
        else:
            flash('Subject already exists', 'error')
    
    subjects = Subject.get_all_subjects()
    
    # Get quizzes grouped by subject
    subjects_with_quizzes = []
    for subject in subjects:
        subject_dict = dict(subject) if hasattr(subject, 'keys') else {
            'id': subject[0], 'name': subject[1], 'description': subject[2], 
            'created_by': subject[3], 'created_at': subject[4], 'creator_name': subject[5]
        }
        quizzes = Quiz.get_quizzes_by_subject(subject_dict['id'])
        # Convert quiz rows to dictionaries
        quiz_list = []
        for quiz in quizzes:
            quiz_dict = dict(quiz) if hasattr(quiz, 'keys') else {
                'id': quiz[0], 'title': quiz[1], 'subject_id': quiz[2], 'creator_id': quiz[3],
                'description': quiz[4], 'difficulty_level': quiz[5], 'time_limit': quiz[6],
                'created_at': quiz[7], 'deadline': quiz[8] if len(quiz) > 8 else None
            }
            quiz_list.append(quiz_dict)
        subject_dict['quizzes'] = quiz_list
        subjects_with_quizzes.append(subject_dict)
    
    return render_template('manage_subjects.html', subjects=subjects_with_quizzes)

@admin_bp.route('/manage_users')
@login_required
def manage_users():
    if session.get('role') != 'teacher':
        flash('Access denied', 'error')
        return redirect(url_for('quiz.home'))
    
    users = User.get_all_users()
    return render_template('manage_users.html', users=users)

@admin_bp.route('/update_user_role', methods=['POST'])
@login_required
def update_user_role():
    if session.get('role') != 'teacher':
        flash('Access denied', 'error')
        return redirect(url_for('quiz.home'))
    
    user_id = request.form['user_id']
    role = request.form['role']
    User.update_user_role(user_id, role)
    flash('User role updated successfully!', 'success')
    return redirect(url_for('admin.manage_users'))

@admin_bp.route('/delete_user/<int:user_id>')
@login_required
def delete_user(user_id):
    if session.get('role') != 'teacher':
        flash('Access denied', 'error')
        return redirect(url_for('quiz.home'))
    
    User.delete_user(user_id)
    flash('User deleted successfully!', 'success')
    return redirect(url_for('admin.manage_users'))
