"""
Enhanced Authentication and Authorization
JWT-based authentication with role-based access control
"""

import jwt
import hashlib
import secrets
import time
from datetime import datetime, timedelta
from functools import wraps
from typing import Optional, Dict, Any, List
from flask import request, jsonify, current_app, session
import logging

logger = logging.getLogger(__name__)

class JWTManager:
    """Enhanced JWT token management with security features"""
    
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
        self.algorithm = 'HS256'
        self.token_blacklist = set()
        self.refresh_tokens = {}
    
    def generate_token_pair(self, user_id: int, role: str, additional_claims: Dict = None) -> Dict[str, str]:
        """Generate access and refresh token pair"""
        now = datetime.utcnow()
        
        # Access token (short-lived)
        access_payload = {
            'user_id': user_id,
            'role': role,
            'type': 'access',
            'iat': now,
            'exp': now + timedelta(hours=1),
            'jti': secrets.token_hex(16)  # Unique token ID
        }
        
        # Add additional claims
        if additional_claims:
            access_payload.update(additional_claims)
        
        # Refresh token (long-lived)
        refresh_payload = {
            'user_id': user_id,
            'type': 'refresh',
            'iat': now,
            'exp': now + timedelta(days=30),
            'jti': secrets.token_hex(16)
        }
        
        access_token = jwt.encode(access_payload, self.secret_key, algorithm=self.algorithm)
        refresh_token = jwt.encode(refresh_payload, self.secret_key, algorithm=self.algorithm)
        
        # Store refresh token
        self.refresh_tokens[refresh_payload['jti']] = {
            'user_id': user_id,
            'created_at': now,
            'expires_at': now + timedelta(days=30)
        }
        
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'expires_in': 3600,  # 1 hour
            'token_type': 'Bearer'
        }
    
    def verify_token(self, token: str, token_type: str = 'access') -> Optional[Dict[str, Any]]:
        """Verify and decode JWT token"""
        try:
            # Check if token is blacklisted
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            if payload.get('jti') in self.token_blacklist:
                logger.warning(f"Blacklisted token used: {payload.get('jti')}")
                return None
            
            if payload.get('type') != token_type:
                logger.warning(f"Invalid token type: expected {token_type}, got {payload.get('type')}")
                return None
            
            return payload
            
        except jwt.ExpiredSignatureError:
            logger.debug("Token expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            return None
    
    def refresh_access_token(self, refresh_token: str) -> Optional[Dict[str, str]]:
        """Generate new access token using refresh token"""
        payload = self.verify_token(refresh_token, 'refresh')
        if not payload:
            return None
        
        jti = payload.get('jti')
        if jti not in self.refresh_tokens:
            logger.warning(f"Invalid refresh token: {jti}")
            return None
        
        # Get user role from database
        from models.user import User
        user = User.get_user_by_id(payload['user_id'])
        if not user:
            logger.warning(f"User not found: {payload['user_id']}")
            return None
        
        # Generate new token pair
        return self.generate_token_pair(user['id'], user['role'])
    
    def blacklist_token(self, token: str) -> bool:
        """Add token to blacklist"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm], options={"verify_exp": False})
            self.token_blacklist.add(payload.get('jti'))
            return True
        except jwt.InvalidTokenError:
            return False
    
    def revoke_refresh_token(self, refresh_token: str) -> bool:
        """Revoke refresh token"""
        payload = self.verify_token(refresh_token, 'refresh')
        if payload:
            jti = payload.get('jti')
            if jti in self.refresh_tokens:
                del self.refresh_tokens[jti]
                return True
        return False
    
    def cleanup_expired_tokens(self):
        """Clean up expired tokens from memory"""
        now = datetime.utcnow()
        
        # Clean expired refresh tokens
        expired_refresh_tokens = [
            jti for jti, data in self.refresh_tokens.items()
            if data['expires_at'] < now
        ]
        
        for jti in expired_refresh_tokens:
            del self.refresh_tokens[jti]
        
        logger.info(f"Cleaned up {len(expired_refresh_tokens)} expired refresh tokens")

class PasswordManager:
    """Enhanced password management with security features"""
    
    @staticmethod
    def hash_password(password: str, salt: str = None) -> tuple:
        """Hash password with salt"""
        if salt is None:
            salt = secrets.token_hex(32)
        
        # Use PBKDF2 with SHA-256
        import hashlib
        password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return password_hash.hex(), salt
    
    @staticmethod
    def verify_password(password: str, password_hash: str, salt: str) -> bool:
        """Verify password against hash"""
        import hashlib
        computed_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return computed_hash.hex() == password_hash
    
    @staticmethod
    def generate_secure_password(length: int = 16) -> str:
        """Generate secure random password"""
        import string
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    @staticmethod
    def validate_password_strength(password: str) -> tuple:
        """Validate password strength"""
        errors = []
        
        if len(password) < 8:
            errors.append("Password must be at least 8 characters long")
        
        if not any(c.isupper() for c in password):
            errors.append("Password must contain at least one uppercase letter")
        
        if not any(c.islower() for c in password):
            errors.append("Password must contain at least one lowercase letter")
        
        if not any(c.isdigit() for c in password):
            errors.append("Password must contain at least one number")
        
        if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            errors.append("Password must contain at least one special character")
        
        # Check for common patterns
        common_patterns = ['123', 'abc', 'qwe', 'password', 'admin', 'user']
        if any(pattern in password.lower() for pattern in common_patterns):
            errors.append("Password contains common patterns")
        
        return len(errors) == 0, errors

class SessionManager:
    """Enhanced session management with security features"""
    
    @staticmethod
    def create_secure_session(user_id: int, role: str, ip_address: str, user_agent: str) -> str:
        """Create secure session with tracking"""
        session_id = secrets.token_urlsafe(32)
        
        # Store session in database
        from config.database_optimized import db_manager
        db_manager.execute_query(
            """INSERT INTO user_sessions (user_id, session_id, ip_address, user_agent, expires_at)
               VALUES (?, ?, ?, ?, ?)""",
            (user_id, session_id, ip_address, user_agent, datetime.utcnow() + timedelta(hours=24))
        )
        
        return session_id
    
    @staticmethod
    def validate_session(session_id: str, ip_address: str) -> Optional[Dict[str, Any]]:
        """Validate session and return user data"""
        from config.database_optimized import db_manager
        from models.user import User
        
        result = db_manager.execute_query(
            """SELECT user_id FROM user_sessions 
               WHERE session_id = ? AND ip_address = ? AND expires_at > CURRENT_TIMESTAMP""",
            (session_id, ip_address),
            fetch='one'
        )
        
        if result:
            user = User.get_user_by_id(result['user_id'])
            return user
        
        return None
    
    @staticmethod
    def destroy_session(session_id: str):
        """Destroy session"""
        from config.database_optimized import db_manager
        db_manager.execute_query(
            "DELETE FROM user_sessions WHERE session_id = ?",
            (session_id,)
        )

# Authentication decorators
def require_auth(f):
    """Require authentication for route"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check for JWT token in Authorization header
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            jwt_manager = JWTManager(current_app.config['SECRET_KEY'])
            payload = jwt_manager.verify_token(token)
            
            if payload:
                request.current_user = payload
                return f(*args, **kwargs)
        
        # Fallback to session-based authentication
        if 'user_id' in session:
            from models.user import User
            user = User.get_user_by_id(session['user_id'])
            if user:
                request.current_user = {'user_id': user['id'], 'role': user['role']}
                return f(*args, **kwargs)
        
        return jsonify({'error': 'Authentication required'}), 401
    
    return decorated_function

def require_role(required_roles: List[str]):
    """Require specific role(s) for route"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not hasattr(request, 'current_user'):
                return jsonify({'error': 'Authentication required'}), 401
            
            user_role = request.current_user.get('role')
            if user_role not in required_roles:
                return jsonify({'error': 'Insufficient permissions'}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def require_admin(f):
    """Require admin role for route"""
    return require_role(['admin'])(f)

def require_teacher(f):
    """Require teacher role for route"""
    return require_role(['teacher', 'admin'])(f)

def require_student(f):
    """Require student role for route"""
    return require_role(['student', 'teacher', 'admin'])(f)

# Rate limiting decorators
def rate_limit(requests_per_minute: int = 60):
    """Rate limiting decorator"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from .rate_limiting import RateLimiter
            rate_limiter = RateLimiter()
            
            client_ip = request.remote_addr
            if not rate_limiter.is_allowed(client_ip, requests_per_minute):
                return jsonify({'error': 'Rate limit exceeded'}), 429
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Security headers decorator
def add_security_headers(f):
    """Add security headers to response"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        response = f(*args, **kwargs)
        
        # Add security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        return response
    return decorated_function

# Audit logging decorator
def audit_log(action: str):
    """Audit logging decorator"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from .audit import AuditLogger
            audit_logger = AuditLogger()
            
            # Log before action
            user_id = getattr(request, 'current_user', {}).get('user_id')
            audit_logger.log_action(user_id, action, 'started', request.remote_addr)
            
            try:
                result = f(*args, **kwargs)
                audit_logger.log_action(user_id, action, 'completed', request.remote_addr)
                return result
            except Exception as e:
                audit_logger.log_action(user_id, action, 'failed', request.remote_addr, str(e))
                raise
        
        return decorated_function
    return decorator

