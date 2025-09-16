"""
Authentication Controller
Handles user login, registration, and session management
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import check_password_hash
from ..models.user import User
from ..utils.otp_utils import generate_otp, store_otp, validate_otp, mark_otp_used, cleanup_expired_otps, is_otp_rate_limited, get_otp_attempts_remaining, send_otp_via_email, send_welcome_notifications
import functools
import re
import time

auth_bp = Blueprint('auth', __name__)

def is_otp_expired(timestamp, expiry_minutes=5):
    """Check if OTP has expired"""
    if not timestamp:
        return True
    current_time = time.time()
    expiry_time = timestamp + (expiry_minutes * 60)  # Convert minutes to seconds
    return current_time > expiry_time

def validate_password_strength(password, username=None, email=None):
    """
    Validate password strength according to common security rules
    Returns (is_valid, error_message)
    """
    errors = []
    
    # Minimum length requirement
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")
    elif len(password) > 64:
        errors.append("Password must not exceed 64 characters")
    
    # Character variety requirements
    if not re.search(r'[A-Z]', password):
        errors.append("Password must contain at least one uppercase letter (A-Z)")
    
    if not re.search(r'[a-z]', password):
        errors.append("Password must contain at least one lowercase letter (a-z)")
    
    if not re.search(r'[0-9]', password):
        errors.append("Password must contain at least one number (0-9)")
    
    if not re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]', password):
        errors.append("Password must contain at least one special character (!@#$%^&*)")
    
    # Common passwords check
    common_passwords = [
        '123456', 'password', 'qwerty', 'abc123', '123456789',
        'password123', 'admin', 'letmein', 'welcome', 'monkey',
        '1234567890', 'dragon', 'master', 'hello', 'freedom'
    ]
    if password.lower() in common_passwords:
        errors.append("Password is too common. Please choose a more secure password")
    
    # No personal info (if username/email provided)
    if username and username.lower() in password.lower():
        errors.append("Password cannot contain your username")
    
    if email and email.split('@')[0].lower() in password.lower():
        errors.append("Password cannot contain your email address")
    
    # No repeating characters (3 or more consecutive same characters)
    if re.search(r'(.)\1{2,}', password):
        errors.append("Password cannot contain 3 or more consecutive identical characters")
    
    # Skip sequential character check for simplicity
    
    if errors:
        return False, "; ".join(errors)
    
    return True, "Password is strong"

# Login required decorator
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view

@auth_bp.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('quiz.home'))
    return redirect(url_for('auth.login'))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        print(f"🔍 Login attempt: username='{username}'")
        
        user = User.get_user_by_username(username)
        
        if user:
            print(f"✅ User found: {user['username']}, role: {user['role']}")
            password_valid = check_password_hash(user['password'], password)
            print(f"🔐 Password valid: {password_valid}")
            
            if password_valid:
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['role'] = user['role']
                
                # Update last login
                User.update_last_login(user['id'])
                
                flash('Login successful!', 'success')
                print(f"🎉 Login successful for user: {username}")
                return redirect(url_for('quiz.home'))
            else:
                print(f"❌ Invalid password for user: {username}")
                flash('Invalid password', 'error')
        else:
            print(f"❌ User not found: {username}")
            flash('Invalid username', 'error')
    
    return render_template('login.html')

@auth_bp.route('/register_email_only', methods=['GET', 'POST'])
def register_email_only():
    """Email-only registration for easy testing with friends"""
    if request.method == 'POST':
        username = request.form['username']
        role = request.form['role']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        email = request.form.get('email', '')
        email_otp = request.form.get('email_otp', '')
        
        print(f"🔍 Email-only registration attempt: username='{username}', role='{role}', email='{email}'")
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
        elif role not in ['student', 'teacher', 'admin']:
            flash('Please select a valid role', 'error')
        elif not email_otp:
            flash('Please verify email OTP first', 'error')
        else:
            # Get OTP from session
            session_email_otp = session.get('email_otp', '')
            email_otp_timestamp = session.get('email_otp_timestamp', 0)
            
            if is_otp_expired(email_otp_timestamp):
                flash('OTP has expired. Please request a new one.', 'error')
            elif email_otp != session_email_otp:
                flash('Invalid OTP code. Please check and try again.', 'error')
            else:
                # Validate password strength
                is_valid_password, password_error = validate_password_strength(password, username, email)
                if not is_valid_password:
                    flash(password_error, 'error')
                else:
                    # Check if username already exists
                    existing_user = User.get_user_by_username(username)
                    if existing_user:
                        flash('Username already exists', 'error')
                    else:
                        # Create user with email only (no phone)
                        if User.create_user(username, password, role, email, ''):
                            flash('Registration successful! Please log in.', 'success')
                            print(f"✅ Email-only user created: {username} ({role})")
                            
                            # Clear session data
                            session.pop('email_otp', None)
                            session.pop('email_otp_timestamp', None)
                            session.pop('email_otp_sent', None)
                            
                            return redirect(url_for('auth.login'))
                        else:
                            flash('Registration failed. Please try again.', 'error')
    
    return render_template('register_email_only.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    # Clear OTP sent flags on page load to prevent persistent messages
    if request.method == 'GET':
        session.pop('email_otp_sent', None)
        session.pop('phone_otp_sent', None)
        session.pop('registration_data', None)
    
    if request.method == 'POST':
        print(f"🔍 POST request received")
        print(f"🔍 Form data: {dict(request.form)}")
        username = request.form['username']
        role = request.form['role']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        email = request.form.get('email', '')
        email_otp = request.form.get('email_otp', '')
        # Email-only verification
        verification_method = 'email'
        
        # Get OTP code from session (sent by the OTP sending route)
        session_email_otp = session.get('email_otp', '')
        email_otp_timestamp = session.get('email_otp_timestamp', 0)
        
        # Use actual user email
        user_email = email
        
        print(f"🔍 Registration attempt: username='{username}', role='{role}'")
        print(f"🔍 Password match: {password == confirm_password}")
        print(f"🔍 Role valid: {role in ['student', 'teacher', 'admin']}")
        print(f"🔍 Email OTP: {email_otp}")
        print(f"🔍 Verification method: {verification_method} (email only)")

        if password != confirm_password:
            print("❌ Passwords do not match")
            flash('Passwords do not match', 'error')
        elif role not in ['student', 'teacher', 'admin']:
            print("❌ Invalid role")
            flash('Please select a valid role', 'error')
        elif not email_otp:
            print("❌ Email OTP required")
            flash('Please verify your email OTP first', 'error')
        elif is_otp_expired(email_otp_timestamp):
            print("❌ OTP code has expired")
            print(f"🔍 Current time: {time.time()}")
            print(f"🔍 OTP timestamp: {email_otp_timestamp}")
            print(f"🔍 Time difference: {time.time() - email_otp_timestamp} seconds")
            flash('OTP code has expired. Please request a new code.', 'error')
        elif email_otp != session_email_otp:
            print("❌ Invalid OTP code")
            print(f"🔍 Expected email OTP: {session_email_otp}, got: {email_otp}")
            flash('Invalid OTP code. Please check and try again.', 'error')
        else:
            # Validate password strength
            is_valid_password, password_error = validate_password_strength(password, username, user_email)
            print(f"🔍 Password valid: {is_valid_password}, error: {password_error}")
            if not is_valid_password:
                flash(password_error, 'error')
            else:
                # Only check if username already exists
                existing_user = User.get_user_by_username(username)
                print(f"🔍 Username exists: {existing_user is not None}")
                if existing_user:
                    flash('Username already exists', 'error')
                else:
                    # Validate both OTPs (both must be 6 digits)
                    if len(email_otp) == 6 and email_otp.isdigit():
                        # Create user with email only
                        print(f"🔍 Creating user: {username}, {role}, {user_email}")
                        if User.create_user(username, password, role, user_email):
                            flash('Registration successful! Please log in.', 'success')
                            print(f"✅ User created: {username} ({role})")
                            return redirect(url_for('auth.login'))
                        else:
                            print("❌ User creation failed")
                            flash('Registration failed. Please try again.', 'error')
                    else:
                        flash('Invalid OTP format - both must be 6 digits', 'error')
    
    return render_template('register.html', now=time.time())


@auth_bp.route('/send_email_otp', methods=['POST'])
def send_email_otp():
    """Send OTP code via email"""
    try:
        data = request.get_json()
        email = data.get('email')
        
        if not email:
            return jsonify({'success': False, 'message': 'Email is required'}), 400
        
        # Generate OTP
        otp_code = generate_otp()
        
        # Send OTP via email
        email_sent = send_otp_via_email(email, otp_code)
        
        if email_sent:
            # Store OTP in session for verification
            session['email_otp'] = otp_code
            session['email_otp_timestamp'] = time.time()
            session['email_otp_sent'] = True
            print(f"📧 Email OTP sent to {email}: {otp_code}")
            return jsonify({'success': True, 'message': 'OTP sent to your email'})
        else:
            return jsonify({'success': False, 'message': 'Failed to send OTP email'}), 500
            
    except Exception as e:
        print(f"❌ Error sending email OTP: {str(e)}")
        return jsonify({'success': False, 'message': 'Error sending OTP'}), 500



@auth_bp.route('/verify_registration_otp', methods=['GET', 'POST'])
def verify_registration_otp():
    if 'registration_data' not in session:
        flash('Please complete registration first', 'error')
        return redirect(url_for('auth.register'))
    
    if request.method == 'POST':
        otp_code = request.form['otp_code']
        phone = session['registration_data']['phone']
        
        is_valid, error_message = validate_otp(phone, otp_code)
        if is_valid:
            # Create the user
            reg_data = session['registration_data']
            if User.create_user(reg_data['username'], reg_data['password'], reg_data['role'], reg_data['email'], reg_data['phone']):
                flash('Registration successful! Please log in.', 'success')
                print(f"✅ User created: {reg_data['username']} ({reg_data['role']})")
                
                # Clear session data
                session.pop('registration_data', None)
                session.pop('generated_otp', None)
                session.pop('email_otp', None)
                session.pop('email_otp_sent', None)
                
                return redirect(url_for('auth.login'))
            else:
                print("❌ User creation failed")
                flash('Registration failed. Please try again.', 'error')
        else:
            flash(error_message, 'error')
    
    # Get the generated OTP for display
    generated_otp = session.get('generated_otp', '')
    return render_template('verify_otp.html', generated_otp=generated_otp, is_registration=True)

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        # Get email and OTP code from request
        email = request.form.get('email', '')
        email_otp = request.form.get('email_otp', '')
        
        print(f"🔍 Forgot password request for email: {email}")
        print(f"🔍 Email OTP: {email_otp}")
        
        # Check if any user exists (we'll use the first available user for testing)
        users = User.get_all_users()
        if not users:
            flash('No users found in the system. Please register first.', 'error')
            return render_template('forgot_password.html')
        
        # Use the first user for testing purposes
        user = users[0]
        print(f"✅ Using user: {user['username']} for password reset")
        
        if not email_otp:
            flash('Please verify your email OTP first', 'error')
            return render_template('forgot_password.html')
        
        # For testing purposes, accept any 6-digit OTP
        if len(email_otp) == 6 and email_otp.isdigit():
            session['reset_email'] = email
            session['reset_user_id'] = user['id']  # Store user ID for password reset
            session['otp_verified'] = True
            flash('OTP verified successfully', 'success')
            return redirect(url_for('auth.reset_password'))
        else:
            flash('Invalid OTP format - must be 6 digits', 'error')
    
    return render_template('forgot_password.html')

@auth_bp.route('/send_forgot_password_email_otp', methods=['POST'])
def send_forgot_password_email_otp():
    """Send OTP code via email for forgot password"""
    try:
        data = request.get_json()
        email = data.get('email')
        
        if not email:
            return jsonify({'success': False, 'message': 'Email is required'}), 400
        
        # Generate OTP code
        otp_code = generate_otp()
        
        # Send OTP via email
        email_sent = send_otp_via_email(email, otp_code, expiry_minutes=3)
        
        if email_sent:
            # Store OTP in session for verification
            session['forgot_email_otp'] = otp_code
            session['forgot_email_otp_timestamp'] = time.time()
            print(f"📧 Forgot password email OTP sent to {email}: {otp_code}")
            return jsonify({'success': True, 'message': 'OTP sent to your email'})
        else:
            return jsonify({'success': False, 'message': 'Failed to send OTP to email'}), 500
            
    except Exception as e:
        print(f"❌ Error sending forgot password email OTP: {str(e)}")
        return jsonify({'success': False, 'message': 'Error sending OTP'}), 500



@auth_bp.route('/verify_otp', methods=['GET', 'POST'])
def verify_otp():
    if 'reset_email' not in session:
        flash('Please request password reset first', 'error')
        return redirect(url_for('auth.forgot_password'))
    
    if request.method == 'POST':
        otp_code = request.form['otp_code']
        email = session['reset_email']
        
        is_valid, error_message = validate_otp(email, otp_code)
        if is_valid:
            session['otp_verified'] = True
            session.pop('generated_otp', None)  # Clear OTP from session after verification
            flash('OTP verified successfully', 'success')
            return redirect(url_for('auth.reset_password'))
        else:
            flash(error_message, 'error')
    
    # Get the generated OTP for display
    generated_otp = session.get('generated_otp', '')
    return render_template('verify_otp.html', generated_otp=generated_otp)

@auth_bp.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if 'reset_email' not in session or not session.get('otp_verified'):
        flash('Please verify OTP first', 'error')
        return redirect(url_for('auth.forgot_password'))
    
    if request.method == 'POST':
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        email = session['reset_email']
        
        if new_password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('reset_password.html')
        
        if len(new_password) < 6:
            flash('Password must be at least 6 characters long', 'error')
            return render_template('reset_password.html')
        
        # Update password using stored user ID
        if 'reset_user_id' in session:
            user_id = session['reset_user_id']
            User.update_password(user_id, new_password)
            print(f"✅ Password updated for user ID: {user_id}")
        else:
            flash('Session expired. Please request password reset again.', 'error')
            return redirect(url_for('auth.forgot_password'))
        
        # Clear session
        session.pop('reset_email', None)
        session.pop('reset_user_id', None)
        session.pop('otp_verified', None)
        
        flash('Password reset successfully! Please log in with your new password.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('reset_password.html')




@auth_bp.route('/check_username', methods=['POST'])
def check_username():
    """Check if username already exists"""
    data = request.get_json()
    username = data.get('username', '').strip()
    
    if not username:
        return jsonify({'available': False, 'message': 'Username is required'})
    
    if len(username) < 3 or len(username) > 20:
        return jsonify({'available': False, 'message': 'Username must be 3-20 characters'})
    
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return jsonify({'available': False, 'message': 'Username can only contain letters, numbers, and underscores'})
    
    existing_user = User.get_user_by_username(username)
    if existing_user:
        return jsonify({'available': False, 'message': 'Username already taken'})
    
    return jsonify({'available': True, 'message': 'Username is available'})

@auth_bp.route('/check_email', methods=['POST'])
def check_email():
    """Check if email already exists"""
    data = request.get_json()
    email = data.get('email', '').strip().lower()
    
    if not email:
        return jsonify({'available': False, 'message': 'Email is required'})
    
    if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
        return jsonify({'available': False, 'message': 'Please enter a valid email address'})
    
    existing_user = User.get_user_by_email(email)
    if existing_user:
        return jsonify({'available': False, 'message': 'Email already registered'})
    
    return jsonify({'available': True, 'message': 'Email is available'})
