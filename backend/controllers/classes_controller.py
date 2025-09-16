"""
Classes Controller
Handles class enrollment and management routes
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from ..models.class_model import Class
from ..models.user import User
from ..models.quiz import Quiz
from ..config.database import get_db_connection
from functools import wraps

classes_bp = Blueprint('classes', __name__)

def login_required(f):
    """Decorator to require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def teacher_required(f):
    """Decorator to require teacher role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'teacher':
            flash('Access denied. Teacher privileges required.', 'error')
            return redirect(url_for('quiz.home'))
        return f(*args, **kwargs)
    return decorated_function

@classes_bp.route('/classes')
@login_required
def view_classes():
    """Display all available classes with enrollment options"""
    user_id = session['user_id']
    role = session['role']
    
    # Get all classes
    classes = Class.get_all_classes()
    
    # For students, get their enrollment status for each class
    if role == 'student':
        for class_item in classes:
            enrollment = Class.get_student_enrollment_status(user_id, class_item['id'])
            class_item['enrollment_status'] = enrollment['status'] if enrollment else None
            class_item['enrollment_date'] = enrollment['requested_at'] if enrollment else None
    
    return render_template('classes.html', classes=classes, role=role)

@classes_bp.route('/enroll/<int:class_id>', methods=['POST'])
@login_required
def enroll_in_class(class_id):
    """Enroll student in a class"""
    if session.get('role') != 'student':
        flash('Only students can enroll in classes', 'error')
        return redirect(url_for('classes.view_classes'))
    
    user_id = session['user_id']
    
    # Check if class exists
    class_info = Class.get_class_by_id(class_id)
    if not class_info:
        flash('Class not found', 'error')
        return redirect(url_for('classes.view_classes'))
    
    # Check if already enrolled
    enrollment = Class.get_student_enrollment_status(user_id, class_id)
    if enrollment:
        if enrollment['status'] == 'pending':
            flash('You already have a pending enrollment request for this class', 'info')
        elif enrollment['status'] == 'approved':
            flash('You are already enrolled in this class', 'info')
        return redirect(url_for('classes.view_classes'))
    
    # Enroll the student
    if Class.enroll_student(user_id, class_id):
        flash(f'Enrollment request sent for {class_info["name"]}! Waiting for teacher approval.', 'success')
    else:
        flash('Failed to send enrollment request. Please try again.', 'error')
    
    return redirect(url_for('classes.view_classes'))

@classes_bp.route('/manage_class/<int:class_id>')
@login_required
@teacher_required
def manage_class(class_id):
    """Manage class enrollments for teachers"""
    teacher_id = session['user_id']
    
    # Check if teacher is assigned to this class
    if not Class.is_teacher_of_class(teacher_id, class_id):
        flash('You are not assigned to this class', 'error')
        return redirect(url_for('quiz.home'))
    
    # Get class information
    class_info = Class.get_class_by_id(class_id)
    if not class_info:
        flash('Class not found', 'error')
        return redirect(url_for('quiz.home'))
    
    # Get pending enrollment requests
    pending_enrollments = Class.get_pending_enrollments_for_class(class_id)
    
    # Get approved students
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT sc.id, sc.student_id, sc.approved_at,
                   u.username, u.email, u.created_at as user_created_at
            FROM student_classes sc
            JOIN users u ON sc.student_id = u.id
            WHERE sc.class_id = ? AND sc.status = 'approved'
            ORDER BY sc.approved_at DESC
        """, (class_id,))
        approved_students = [dict(row) for row in cursor.fetchall()]
    except Exception as e:
        print(f"Error getting approved students: {e}")
        approved_students = []
    finally:
        conn.close()
    
    return render_template('manage_class.html', 
                         class_info=class_info,
                         pending_enrollments=pending_enrollments,
                         approved_students=approved_students)

@classes_bp.route('/approve_student/<int:class_id>/<int:student_id>', methods=['POST'])
@login_required
@teacher_required
def approve_student(class_id, student_id):
    """Approve a student's enrollment request"""
    teacher_id = session['user_id']
    
    # Check if teacher is assigned to this class
    if not Class.is_teacher_of_class(teacher_id, class_id):
        flash('You are not assigned to this class', 'error')
        return redirect(url_for('quiz.home'))
    
    # Get student and class info for flash message
    student = User.get_user_by_id(student_id)
    class_info = Class.get_class_by_id(class_id)
    
    if Class.approve_student(student_id, class_id):
        flash(f'Student {student["username"]} has been approved for {class_info["name"]}!', 'success')
    else:
        flash('Failed to approve student. Please try again.', 'error')
    
    return redirect(url_for('classes.manage_class', class_id=class_id))

@classes_bp.route('/reject_student/<int:class_id>/<int:student_id>', methods=['POST'])
@login_required
@teacher_required
def reject_student(class_id, student_id):
    """Reject a student's enrollment request"""
    teacher_id = session['user_id']
    
    # Check if teacher is assigned to this class
    if not Class.is_teacher_of_class(teacher_id, class_id):
        flash('You are not assigned to this class', 'error')
        return redirect(url_for('quiz.home'))
    
    # Get student and class info for flash message
    student = User.get_user_by_id(student_id)
    class_info = Class.get_class_by_id(class_id)
    
    if Class.reject_student(student_id, class_id):
        flash(f'Student {student["username"]} enrollment request has been rejected for {class_info["name"]}.', 'info')
    else:
        flash('Failed to reject student. Please try again.', 'error')
    
    return redirect(url_for('classes.manage_class', class_id=class_id))

@classes_bp.route('/my_classes')
@login_required
def my_classes():
    """Show user's enrolled classes (students) or assigned classes (teachers)"""
    user_id = session['user_id']
    role = session['role']
    
    if role == 'student':
        classes = Class.get_classes_for_student(user_id)
        return render_template('my_classes.html', classes=classes, role=role)
    elif role == 'teacher':
        classes = Class.get_classes_for_teacher(user_id)
        return render_template('my_classes.html', classes=classes, role=role)
    else:
        flash('Invalid user role', 'error')
        return redirect(url_for('quiz.home'))

@classes_bp.route('/enrollment_requests')
@login_required
def enrollment_requests():
    """Show pending enrollment requests for teachers"""
    if session.get('role') not in ['teacher', 'admin']:
        flash('Access denied', 'error')
        return redirect(url_for('quiz.home'))
    
    pending_requests = Class.get_pending_enrollments()
    return render_template('enrollment_requests.html', pending_requests=pending_requests)

@classes_bp.route('/approve_enrollment/<int:student_id>/<int:class_id>')
@login_required
def approve_enrollment(student_id, class_id):
    """Approve a student's enrollment request"""
    if session.get('role') not in ['teacher', 'admin']:
        flash('Access denied', 'error')
        return redirect(url_for('quiz.home'))
    
    if Class.approve_student(student_id, class_id):
        flash('Student enrollment approved!', 'success')
    else:
        flash('Failed to approve enrollment', 'error')
    
    return redirect(url_for('classes.enrollment_requests'))

@classes_bp.route('/reject_enrollment/<int:student_id>/<int:class_id>')
@login_required
def reject_enrollment(student_id, class_id):
    """Reject a student's enrollment request"""
    if session.get('role') not in ['teacher', 'admin']:
        flash('Access denied', 'error')
        return redirect(url_for('quiz.home'))
    
    if Class.reject_student(student_id, class_id):
        flash('Student enrollment rejected', 'info')
    else:
        flash('Failed to reject enrollment', 'error')
    
    return redirect(url_for('classes.enrollment_requests'))

@classes_bp.route('/view_class/<int:class_id>')
@login_required
def view_class(class_id):
    """View details of a specific class"""
    if session.get('role') not in ['teacher', 'admin']:
        flash('Access denied', 'error')
        return redirect(url_for('quiz.home'))
    
    class_info = Class.get_class_by_id(class_id)
    if not class_info:
        flash('Class not found', 'error')
        return redirect(url_for('classes.my_classes'))
    
    # Get students enrolled in this class
    students = Class.get_students_in_class(class_id)
    
    # Get pending requests for this class
    pending_requests = Class.get_pending_enrollments_for_class(class_id)
    
    return render_template('view_class.html', 
                         class_info=class_info, 
                         students=students,
                         pending_requests=pending_requests)
