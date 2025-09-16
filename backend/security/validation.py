"""
Enhanced Input Validation and Sanitization
Comprehensive validation for all user inputs
"""

import re
import bleach
import html
from typing import Any, Dict, List, Optional, Union
from marshmallow import Schema, fields, validate, ValidationError, post_load
from marshmallow.decorators import validates_schema
import logging

logger = logging.getLogger(__name__)

class InputValidator:
    """Enhanced input validation with security features"""
    
    # Common validation patterns
    PATTERNS = {
        'username': re.compile(r'^[a-zA-Z0-9_]{3,50}$'),
        'email': re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'),
        'phone': re.compile(r'^\+?[1-9]\d{1,14}$'),
        'password': re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,128}$'),
        'alphanumeric': re.compile(r'^[a-zA-Z0-9\s]+$'),
        'numeric': re.compile(r'^\d+$'),
        'url': re.compile(r'^https?://[^\s/$.?#].[^\s]*$'),
        'filename': re.compile(r'^[a-zA-Z0-9._-]+$')
    }
    
    # Dangerous patterns to block
    DANGEROUS_PATTERNS = [
        r'<script[^>]*>.*?</script>',
        r'javascript:',
        r'vbscript:',
        r'onload\s*=',
        r'onerror\s*=',
        r'onclick\s*=',
        r'<iframe[^>]*>',
        r'<object[^>]*>',
        r'<embed[^>]*>',
        r'<link[^>]*>',
        r'<meta[^>]*>',
        r'<style[^>]*>',
        r'expression\s*\(',
        r'url\s*\(',
        r'@import',
        r'\.\./',
        r'\.\.\\',
        r'%2e%2e%2f',
        r'%2e%2e%5c'
    ]
    
    @classmethod
    def validate_username(cls, username: str) -> tuple:
        """Validate username"""
        if not username:
            return False, "Username is required"
        
        if not cls.PATTERNS['username'].match(username):
            return False, "Username must be 3-50 characters long and contain only letters, numbers, and underscores"
        
        # Check for reserved usernames
        reserved_usernames = ['admin', 'administrator', 'root', 'system', 'api', 'www', 'mail', 'ftp']
        if username.lower() in reserved_usernames:
            return False, "Username is reserved"
        
        return True, "Valid username"
    
    @classmethod
    def validate_email(cls, email: str) -> tuple:
        """Validate email address"""
        if not email:
            return False, "Email is required"
        
        if not cls.PATTERNS['email'].match(email):
            return False, "Invalid email format"
        
        # Check for disposable email domains
        disposable_domains = ['10minutemail.com', 'tempmail.org', 'guerrillamail.com']
        domain = email.split('@')[1].lower()
        if domain in disposable_domains:
            return False, "Disposable email addresses are not allowed"
        
        return True, "Valid email"
    
    @classmethod
    def validate_phone(cls, phone: str) -> tuple:
        """Validate phone number"""
        if not phone:
            return False, "Phone number is required"
        
        if not cls.PATTERNS['phone'].match(phone):
            return False, "Invalid phone number format"
        
        return True, "Valid phone number"
    
    @classmethod
    def validate_password(cls, password: str) -> tuple:
        """Validate password strength"""
        if not password:
            return False, "Password is required"
        
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        
        if len(password) > 128:
            return False, "Password must be less than 128 characters"
        
        if not cls.PATTERNS['password'].match(password):
            return False, "Password must contain uppercase, lowercase, number, and special character"
        
        # Check for common passwords
        common_passwords = [
            'password', '123456', '123456789', 'qwerty', 'abc123',
            'password123', 'admin', 'letmein', 'welcome', 'monkey'
        ]
        if password.lower() in common_passwords:
            return False, "Password is too common"
        
        return True, "Valid password"
    
    @classmethod
    def validate_text_input(cls, text: str, max_length: int = 1000, allow_html: bool = False) -> tuple:
        """Validate general text input"""
        if not text:
            return False, "Text is required"
        
        if len(text) > max_length:
            return False, f"Text must be less than {max_length} characters"
        
        # Check for dangerous patterns
        for pattern in cls.DANGEROUS_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                return False, "Text contains potentially dangerous content"
        
        if not allow_html:
            # Check for HTML tags
            if re.search(r'<[^>]+>', text):
                return False, "HTML tags are not allowed"
        
        return True, "Valid text"
    
    @classmethod
    def validate_file_upload(cls, filename: str, allowed_extensions: List[str], max_size: int = 16777216) -> tuple:
        """Validate file upload"""
        if not filename:
            return False, "Filename is required"
        
        # Check filename pattern
        if not cls.PATTERNS['filename'].match(filename):
            return False, "Invalid filename"
        
        # Check file extension
        extension = filename.split('.')[-1].lower()
        if extension not in allowed_extensions:
            return False, f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}"
        
        # Check for dangerous extensions
        dangerous_extensions = ['exe', 'bat', 'cmd', 'com', 'pif', 'scr', 'vbs', 'js', 'jar']
        if extension in dangerous_extensions:
            return False, "File type is not allowed for security reasons"
        
        return True, "Valid file"
    
    @classmethod
    def validate_numeric_input(cls, value: Union[str, int], min_val: int = 0, max_val: int = 999999) -> tuple:
        """Validate numeric input"""
        try:
            num_value = int(value)
            if num_value < min_val or num_value > max_val:
                return False, f"Value must be between {min_val} and {max_val}"
            return True, "Valid number"
        except (ValueError, TypeError):
            return False, "Invalid number format"

def sanitize_input(data: Any, allow_html: bool = False) -> Any:
    """Sanitize user input to prevent XSS and other attacks"""
    if isinstance(data, str):
        if allow_html:
            # Allow safe HTML tags
            allowed_tags = ['b', 'i', 'em', 'strong', 'p', 'br', 'ul', 'ol', 'li']
            allowed_attributes = {}
            return bleach.clean(data, tags=allowed_tags, attributes=allowed_attributes)
        else:
            # Remove all HTML tags and escape special characters
            return html.escape(bleach.clean(data, tags=[], strip=True))
    
    elif isinstance(data, dict):
        return {key: sanitize_input(value, allow_html) for key, value in data.items()}
    
    elif isinstance(data, list):
        return [sanitize_input(item, allow_html) for item in data]
    
    return data

# Marshmallow Schemas for API validation
class UserRegistrationSchema(Schema):
    """User registration validation schema"""
    username = fields.Str(
        required=True,
        validate=[
            validate.Length(min=3, max=50),
            validate.Regexp(InputValidator.PATTERNS['username'], error='Invalid username format')
        ]
    )
    password = fields.Str(
        required=True,
        validate=[
            validate.Length(min=8, max=128),
            validate.Regexp(InputValidator.PATTERNS['password'], error='Password must contain uppercase, lowercase, number, and special character')
        ]
    )
    email = fields.Email(
        required=True,
        validate=validate.Email(error='Invalid email format')
    )
    phone = fields.Str(
        required=True,
        validate=validate.Regexp(InputValidator.PATTERNS['phone'], error='Invalid phone format')
    )
    role = fields.Str(
        required=True,
        validate=validate.OneOf(['student', 'teacher'], error='Invalid role')
    )
    
    @validates_schema
    def validate_username_not_reserved(self, data, **kwargs):
        """Validate username is not reserved"""
        username = data.get('username', '').lower()
        reserved_usernames = ['admin', 'administrator', 'root', 'system', 'api', 'www', 'mail', 'ftp']
        if username in reserved_usernames:
            raise ValidationError('Username is reserved', 'username')
    
    @validates_schema
    def validate_email_not_disposable(self, data, **kwargs):
        """Validate email is not disposable"""
        email = data.get('email', '')
        domain = email.split('@')[1].lower() if '@' in email else ''
        disposable_domains = ['10minutemail.com', 'tempmail.org', 'guerrillamail.com']
        if domain in disposable_domains:
            raise ValidationError('Disposable email addresses are not allowed', 'email')

class QuizCreationSchema(Schema):
    """Quiz creation validation schema"""
    title = fields.Str(
        required=True,
        validate=[
            validate.Length(min=1, max=200),
            validate.Regexp(InputValidator.PATTERNS['alphanumeric'], error='Title contains invalid characters')
        ]
    )
    description = fields.Str(
        required=False,
        validate=validate.Length(max=1000)
    )
    subject_id = fields.Int(
        required=True,
        validate=validate.Range(min=1, error='Invalid subject ID')
    )
    difficulty_level = fields.Str(
        required=True,
        validate=validate.OneOf(['beginner', 'intermediate', 'advanced'], error='Invalid difficulty level')
    )
    time_limit = fields.Int(
        required=False,
        validate=validate.Range(min=0, max=300, error='Time limit must be between 0 and 300 minutes')
    )

class QuestionCreationSchema(Schema):
    """Question creation validation schema"""
    question_text = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=1000)
    )
    option1 = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=500)
    )
    option2 = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=500)
    )
    option3 = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=500)
    )
    option4 = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=500)
    )
    correct_option = fields.Int(
        required=True,
        validate=validate.Range(min=1, max=4, error='Correct option must be between 1 and 4')
    )
    explanation = fields.Str(
        required=False,
        validate=validate.Length(max=1000)
    )

class ClassEnrollmentSchema(Schema):
    """Class enrollment validation schema"""
    class_id = fields.Int(
        required=True,
        validate=validate.Range(min=1, error='Invalid class ID')
    )

class PasswordResetSchema(Schema):
    """Password reset validation schema"""
    email = fields.Email(
        required=True,
        validate=validate.Email(error='Invalid email format')
    )

class PasswordChangeSchema(Schema):
    """Password change validation schema"""
    current_password = fields.Str(required=True)
    new_password = fields.Str(
        required=True,
        validate=[
            validate.Length(min=8, max=128),
            validate.Regexp(InputValidator.PATTERNS['password'], error='Password must contain uppercase, lowercase, number, and special character')
        ]
    )
    confirm_password = fields.Str(required=True)
    
    @validates_schema
    def validate_passwords_match(self, data, **kwargs):
        """Validate passwords match"""
        if data.get('new_password') != data.get('confirm_password'):
            raise ValidationError('Passwords do not match', 'confirm_password')

class ProfileUpdateSchema(Schema):
    """Profile update validation schema"""
    full_name = fields.Str(
        required=False,
        validate=[
            validate.Length(min=1, max=100),
            validate.Regexp(InputValidator.PATTERNS['alphanumeric'], error='Name contains invalid characters')
        ]
    )
    email = fields.Email(
        required=False,
        validate=validate.Email(error='Invalid email format')
    )
    phone = fields.Str(
        required=False,
        validate=validate.Regexp(InputValidator.PATTERNS['phone'], error='Invalid phone format')
    )

# Validation decorators
def validate_input(schema_class):
    """Decorator to validate input using Marshmallow schema"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from flask import request
            
            # Get data from request
            if request.is_json:
                data = request.get_json()
            else:
                data = request.form.to_dict()
            
            # Validate data
            schema = schema_class()
            try:
                validated_data = schema.load(data)
                request.validated_data = validated_data
                return f(*args, **kwargs)
            except ValidationError as e:
                return jsonify({'error': 'Validation failed', 'details': e.messages}), 400
        
        return decorated_function
    return decorator

def sanitize_request_data(allow_html: bool = False):
    """Decorator to sanitize request data"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from flask import request
            
            # Sanitize form data
            if request.form:
                request.form = sanitize_input(request.form.to_dict(), allow_html)
            
            # Sanitize JSON data
            if request.is_json:
                request.json = sanitize_input(request.get_json(), allow_html)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Content Security Policy
def get_csp_header() -> str:
    """Generate Content Security Policy header"""
    return (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval' cdn.jsdelivr.net; "
        "style-src 'self' 'unsafe-inline' cdn.jsdelivr.net; "
        "img-src 'self' data: https:; "
        "font-src 'self' cdn.jsdelivr.net; "
        "connect-src 'self'; "
        "frame-ancestors 'none'; "
        "base-uri 'self'; "
        "form-action 'self'"
    )

