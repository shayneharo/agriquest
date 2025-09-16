"""
Security Tests
Unit tests for security components
"""

import pytest
import jwt
from datetime import datetime, timedelta
from backend.security.auth import JWTManager, PasswordManager, SessionManager
from backend.security.validation import InputValidator, sanitize_input
from backend.security.rate_limiting import RateLimiter, AdvancedRateLimiter
from backend.security.audit import AuditLogger, AuditEventType, AuditSeverity

class TestJWTManager:
    """Test JWT token management"""
    
    def test_generate_token_pair(self):
        """Test token pair generation"""
        jwt_manager = JWTManager('test-secret-key')
        
        token_pair = jwt_manager.generate_token_pair(1, 'student')
        
        assert 'access_token' in token_pair
        assert 'refresh_token' in token_pair
        assert 'expires_in' in token_pair
        assert 'token_type' in token_pair
        assert token_pair['token_type'] == 'Bearer'
        assert token_pair['expires_in'] == 3600
    
    def test_verify_valid_token(self):
        """Test verifying valid token"""
        jwt_manager = JWTManager('test-secret-key')
        
        token_pair = jwt_manager.generate_token_pair(1, 'student')
        payload = jwt_manager.verify_token(token_pair['access_token'])
        
        assert payload is not None
        assert payload['user_id'] == 1
        assert payload['role'] == 'student'
        assert payload['type'] == 'access'
    
    def test_verify_invalid_token(self):
        """Test verifying invalid token"""
        jwt_manager = JWTManager('test-secret-key')
        
        payload = jwt_manager.verify_token('invalid-token')
        assert payload is None
    
    def test_verify_expired_token(self):
        """Test verifying expired token"""
        jwt_manager = JWTManager('test-secret-key')
        
        # Create expired token
        expired_payload = {
            'user_id': 1,
            'role': 'student',
            'type': 'access',
            'iat': datetime.utcnow() - timedelta(hours=2),
            'exp': datetime.utcnow() - timedelta(hours=1)
        }
        
        expired_token = jwt.encode(expired_payload, 'test-secret-key', algorithm='HS256')
        payload = jwt_manager.verify_token(expired_token)
        
        assert payload is None
    
    def test_blacklist_token(self):
        """Test token blacklisting"""
        jwt_manager = JWTManager('test-secret-key')
        
        token_pair = jwt_manager.generate_token_pair(1, 'student')
        access_token = token_pair['access_token']
        
        # Verify token is valid
        payload = jwt_manager.verify_token(access_token)
        assert payload is not None
        
        # Blacklist token
        result = jwt_manager.blacklist_token(access_token)
        assert result is True
        
        # Verify token is now invalid
        payload = jwt_manager.verify_token(access_token)
        assert payload is None
    
    def test_refresh_token(self):
        """Test token refresh"""
        jwt_manager = JWTManager('test-secret-key')
        
        token_pair = jwt_manager.generate_token_pair(1, 'student')
        refresh_token = token_pair['refresh_token']
        
        # Refresh token
        new_token_pair = jwt_manager.refresh_access_token(refresh_token)
        
        assert new_token_pair is not None
        assert 'access_token' in new_token_pair
        assert 'refresh_token' in new_token_pair

class TestPasswordManager:
    """Test password management"""
    
    def test_hash_password(self):
        """Test password hashing"""
        password = 'TestPassword123!'
        password_hash, salt = PasswordManager.hash_password(password)
        
        assert password_hash is not None
        assert salt is not None
        assert len(password_hash) == 64  # SHA-256 hex length
        assert len(salt) == 64  # 32 bytes hex encoded
    
    def test_verify_password(self):
        """Test password verification"""
        password = 'TestPassword123!'
        password_hash, salt = PasswordManager.hash_password(password)
        
        # Verify correct password
        result = PasswordManager.verify_password(password, password_hash, salt)
        assert result is True
        
        # Verify incorrect password
        result = PasswordManager.verify_password('WrongPassword', password_hash, salt)
        assert result is False
    
    def test_generate_secure_password(self):
        """Test secure password generation"""
        password = PasswordManager.generate_secure_password(16)
        
        assert len(password) == 16
        assert any(c.isupper() for c in password)
        assert any(c.islower() for c in password)
        assert any(c.isdigit() for c in password)
        assert any(c in "!@#$%^&*" for c in password)
    
    def test_validate_password_strength(self):
        """Test password strength validation"""
        # Valid password
        is_valid, errors = PasswordManager.validate_password_strength('TestPassword123!')
        assert is_valid is True
        assert len(errors) == 0
        
        # Weak password
        is_valid, errors = PasswordManager.validate_password_strength('weak')
        assert is_valid is False
        assert len(errors) > 0
        
        # Password too short
        is_valid, errors = PasswordManager.validate_password_strength('Test1!')
        assert is_valid is False
        assert any('8 characters' in error for error in errors)
        
        # Missing uppercase
        is_valid, errors = PasswordManager.validate_password_strength('testpassword123!')
        assert is_valid is False
        assert any('uppercase' in error for error in errors)
        
        # Missing lowercase
        is_valid, errors = PasswordManager.validate_password_strength('TESTPASSWORD123!')
        assert is_valid is False
        assert any('lowercase' in error for error in errors)
        
        # Missing number
        is_valid, errors = PasswordManager.validate_password_strength('TestPassword!')
        assert is_valid is False
        assert any('number' in error for error in errors)
        
        # Missing special character
        is_valid, errors = PasswordManager.validate_password_strength('TestPassword123')
        assert is_valid is False
        assert any('special character' in error for error in errors)

class TestInputValidator:
    """Test input validation"""
    
    def test_validate_username(self):
        """Test username validation"""
        # Valid username
        is_valid, message = InputValidator.validate_username('testuser123')
        assert is_valid is True
        
        # Too short
        is_valid, message = InputValidator.validate_username('ab')
        assert is_valid is False
        
        # Too long
        is_valid, message = InputValidator.validate_username('a' * 51)
        assert is_valid is False
        
        # Invalid characters
        is_valid, message = InputValidator.validate_username('test-user!')
        assert is_valid is False
        
        # Reserved username
        is_valid, message = InputValidator.validate_username('admin')
        assert is_valid is False
    
    def test_validate_email(self):
        """Test email validation"""
        # Valid email
        is_valid, message = InputValidator.validate_email('test@example.com')
        assert is_valid is True
        
        # Invalid format
        is_valid, message = InputValidator.validate_email('invalid-email')
        assert is_valid is False
        
        # Disposable email
        is_valid, message = InputValidator.validate_email('test@10minutemail.com')
        assert is_valid is False
    
    def test_validate_phone(self):
        """Test phone validation"""
        # Valid phone
        is_valid, message = InputValidator.validate_phone('+1234567890')
        assert is_valid is True
        
        # Invalid format
        is_valid, message = InputValidator.validate_phone('123-456-7890')
        assert is_valid is False
    
    def test_validate_password(self):
        """Test password validation"""
        # Valid password
        is_valid, message = InputValidator.validate_password('TestPassword123!')
        assert is_valid is True
        
        # Too short
        is_valid, message = InputValidator.validate_password('Test1!')
        assert is_valid is False
        
        # Too long
        is_valid, message = InputValidator.validate_password('A' * 129 + '1!')
        assert is_valid is False
        
        # Missing requirements
        is_valid, message = InputValidator.validate_password('testpassword')
        assert is_valid is False
        
        # Common password
        is_valid, message = InputValidator.validate_password('password123')
        assert is_valid is False
    
    def test_validate_text_input(self):
        """Test text input validation"""
        # Valid text
        is_valid, message = InputValidator.validate_text_input('This is valid text')
        assert is_valid is True
        
        # Too long
        is_valid, message = InputValidator.validate_text_input('a' * 1001)
        assert is_valid is False
        
        # Contains HTML
        is_valid, message = InputValidator.validate_text_input('<script>alert("xss")</script>')
        assert is_valid is False
        
        # Contains dangerous pattern
        is_valid, message = InputValidator.validate_text_input('javascript:alert("xss")')
        assert is_valid is False
    
    def test_validate_file_upload(self):
        """Test file upload validation"""
        # Valid file
        is_valid, message = InputValidator.validate_file_upload('document.pdf', ['pdf', 'doc', 'docx'])
        assert is_valid is True
        
        # Invalid extension
        is_valid, message = InputValidator.validate_file_upload('document.txt', ['pdf', 'doc', 'docx'])
        assert is_valid is False
        
        # Dangerous extension
        is_valid, message = InputValidator.validate_file_upload('malware.exe', ['pdf', 'doc', 'docx'])
        assert is_valid is False
        
        # Invalid filename
        is_valid, message = InputValidator.validate_file_upload('file with spaces.pdf', ['pdf'])
        assert is_valid is False

class TestSanitization:
    """Test input sanitization"""
    
    def test_sanitize_text(self):
        """Test text sanitization"""
        # HTML tags removed
        result = sanitize_input('<script>alert("xss")</script>')
        assert '<script>' not in result
        assert 'alert' not in result
        
        # Special characters escaped
        result = sanitize_input('Test & "quotes"')
        assert '&amp;' in result
        assert '&quot;' in result
    
    def test_sanitize_dict(self):
        """Test dictionary sanitization"""
        data = {
            'name': '<script>alert("xss")</script>',
            'description': 'Normal text'
        }
        
        result = sanitize_input(data)
        assert '<script>' not in result['name']
        assert result['description'] == 'Normal text'
    
    def test_sanitize_list(self):
        """Test list sanitization"""
        data = ['<script>alert("xss")</script>', 'Normal text']
        
        result = sanitize_input(data)
        assert '<script>' not in result[0]
        assert result[1] == 'Normal text'

class TestRateLimiting:
    """Test rate limiting functionality"""
    
    def test_rate_limiter_allow(self):
        """Test rate limiter allows requests within limit"""
        rate_limiter = RateLimiter()
        
        # Should allow requests within limit
        for i in range(5):
            is_allowed, info = rate_limiter.is_allowed('test-ip', 'login')
            assert is_allowed is True
    
    def test_rate_limiter_block(self):
        """Test rate limiter blocks requests over limit"""
        rate_limiter = RateLimiter()
        
        # Exceed rate limit
        for i in range(6):
            is_allowed, info = rate_limiter.is_allowed('test-ip', 'login')
        
        # Should be blocked
        assert is_allowed is False
        assert info['retry_after'] > 0
    
    def test_advanced_rate_limiter_ip_blocking(self):
        """Test advanced rate limiter IP blocking"""
        rate_limiter = AdvancedRateLimiter()
        
        # Block IP
        rate_limiter.block_ip('test-ip', 60)
        
        # Should be blocked
        is_allowed, info = rate_limiter.is_allowed('test-ip', 'general')
        assert is_allowed is False
        assert info['blocked'] is True
    
    def test_advanced_rate_limiter_whitelist(self):
        """Test advanced rate limiter whitelist"""
        rate_limiter = AdvancedRateLimiter()
        
        # Whitelist IP
        rate_limiter.whitelist.add('whitelisted-ip')
        
        # Should be allowed regardless of rate limit
        is_allowed, info = rate_limiter.is_allowed('whitelisted-ip', 'general')
        assert is_allowed is True
        assert info['whitelisted'] is True

class TestAuditLogging:
    """Test audit logging functionality"""
    
    def test_audit_logger_creation(self):
        """Test audit logger creation"""
        audit_logger = AuditLogger()
        assert audit_logger is not None
    
    def test_log_authentication(self):
        """Test authentication logging"""
        audit_logger = AuditLogger()
        
        # Log successful authentication
        audit_logger.log_authentication(
            user_id=1,
            action='login',
            success=True,
            details={'method': 'password'}
        )
        
        # Log failed authentication
        audit_logger.log_authentication(
            user_id=None,
            action='login',
            success=False,
            details={'method': 'password'},
            error_message='Invalid credentials'
        )
    
    def test_log_authorization(self):
        """Test authorization logging"""
        audit_logger = AuditLogger()
        
        audit_logger.log_authorization(
            user_id=1,
            action='access_quiz',
            resource='quiz:123',
            success=True,
            details={'quiz_id': 123}
        )
    
    def test_log_data_modification(self):
        """Test data modification logging"""
        audit_logger = AuditLogger()
        
        audit_logger.log_data_modification(
            user_id=1,
            action='update_quiz',
            resource_type='quiz',
            resource_id=123,
            old_data={'title': 'Old Title'},
            new_data={'title': 'New Title'}
        )
    
    def test_log_security_event(self):
        """Test security event logging"""
        audit_logger = AuditLogger()
        
        audit_logger.log_security_event(
            event_type='suspicious_activity',
            severity=AuditSeverity.HIGH,
            details={'ip_address': '192.168.1.1', 'activity': 'multiple_failed_logins'}
        )
    
    def test_log_admin_action(self):
        """Test admin action logging"""
        audit_logger = AuditLogger()
        
        audit_logger.log_admin_action(
            admin_id=1,
            action='delete_user',
            target_user_id=2,
            details={'reason': 'policy_violation'}
        )

