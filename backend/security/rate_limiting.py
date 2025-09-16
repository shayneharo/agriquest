"""
Rate Limiting Implementation
Protection against abuse and DDoS attacks
"""

import time
import redis
import logging
from typing import Dict, Optional, Tuple
from functools import wraps
from flask import request, jsonify, current_app
from collections import defaultdict, deque
import threading

logger = logging.getLogger(__name__)

class RateLimiter:
    """Advanced rate limiting with multiple strategies"""
    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        self.redis_client = redis_client
        self.memory_store = defaultdict(lambda: deque())
        self.lock = threading.Lock()
        
        # Rate limiting configurations
        self.limits = {
            'login': {'requests': 5, 'window': 300},  # 5 attempts per 5 minutes
            'register': {'requests': 3, 'window': 3600},  # 3 attempts per hour
            'password_reset': {'requests': 3, 'window': 3600},  # 3 attempts per hour
            'api': {'requests': 100, 'window': 60},  # 100 requests per minute
            'general': {'requests': 1000, 'window': 3600},  # 1000 requests per hour
            'upload': {'requests': 10, 'window': 3600},  # 10 uploads per hour
            'quiz_submit': {'requests': 50, 'window': 3600},  # 50 quiz submissions per hour
        }
    
    def is_allowed(self, identifier: str, limit_type: str = 'general', custom_limit: Optional[Dict] = None) -> Tuple[bool, Dict]:
        """Check if request is allowed based on rate limit"""
        limit_config = custom_limit or self.limits.get(limit_type, self.limits['general'])
        requests_limit = limit_config['requests']
        window_seconds = limit_config['window']
        
        current_time = time.time()
        
        if self.redis_client:
            return self._check_redis_limit(identifier, limit_type, requests_limit, window_seconds, current_time)
        else:
            return self._check_memory_limit(identifier, limit_type, requests_limit, window_seconds, current_time)
    
    def _check_redis_limit(self, identifier: str, limit_type: str, requests_limit: int, window_seconds: int, current_time: float) -> Tuple[bool, Dict]:
        """Check rate limit using Redis"""
        try:
            key = f"rate_limit:{limit_type}:{identifier}"
            
            # Use Redis pipeline for atomic operations
            pipe = self.redis_client.pipeline()
            
            # Remove expired entries
            pipe.zremrangebyscore(key, 0, current_time - window_seconds)
            
            # Count current requests
            pipe.zcard(key)
            
            # Add current request
            pipe.zadd(key, {str(current_time): current_time})
            
            # Set expiration
            pipe.expire(key, window_seconds)
            
            results = pipe.execute()
            current_requests = results[1]
            
            is_allowed = current_requests < requests_limit
            
            return is_allowed, {
                'limit': requests_limit,
                'remaining': max(0, requests_limit - current_requests - 1),
                'reset_time': int(current_time + window_seconds),
                'retry_after': window_seconds if not is_allowed else 0
            }
            
        except Exception as e:
            logger.error(f"Redis rate limiting error: {e}")
            # Fallback to memory-based limiting
            return self._check_memory_limit(identifier, limit_type, requests_limit, window_seconds, current_time)
    
    def _check_memory_limit(self, identifier: str, limit_type: str, requests_limit: int, window_seconds: int, current_time: float) -> Tuple[bool, Dict]:
        """Check rate limit using in-memory storage"""
        with self.lock:
            key = f"{limit_type}:{identifier}"
            request_times = self.memory_store[key]
            
            # Remove expired entries
            while request_times and request_times[0] <= current_time - window_seconds:
                request_times.popleft()
            
            # Check if limit exceeded
            is_allowed = len(request_times) < requests_limit
            
            if is_allowed:
                request_times.append(current_time)
            
            return is_allowed, {
                'limit': requests_limit,
                'remaining': max(0, requests_limit - len(request_times)),
                'reset_time': int(current_time + window_seconds),
                'retry_after': window_seconds if not is_allowed else 0
            }
    
    def get_client_identifier(self, request) -> str:
        """Get unique identifier for rate limiting"""
        # Try to get user ID from session or JWT
        if hasattr(request, 'current_user') and request.current_user:
            return f"user:{request.current_user.get('user_id')}"
        
        # Fallback to IP address
        return f"ip:{request.remote_addr}"
    
    def cleanup_expired_entries(self):
        """Clean up expired entries from memory store"""
        current_time = time.time()
        with self.lock:
            for key, request_times in list(self.memory_store.items()):
                # Remove expired entries
                while request_times and request_times[0] <= current_time - 3600:  # 1 hour cleanup
                    request_times.popleft()
                
                # Remove empty entries
                if not request_times:
                    del self.memory_store[key]

class AdvancedRateLimiter(RateLimiter):
    """Advanced rate limiter with additional features"""
    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        super().__init__(redis_client)
        self.blocked_ips = set()
        self.suspicious_ips = defaultdict(int)
        self.whitelist = set()
        self.blacklist = set()
    
    def is_ip_blocked(self, ip_address: str) -> bool:
        """Check if IP is blocked"""
        return ip_address in self.blocked_ips or ip_address in self.blacklist
    
    def is_ip_whitelisted(self, ip_address: str) -> bool:
        """Check if IP is whitelisted"""
        return ip_address in self.whitelist
    
    def block_ip(self, ip_address: str, duration: int = 3600):
        """Block IP address for specified duration"""
        self.blocked_ips.add(ip_address)
        
        # Schedule unblock
        def unblock():
            time.sleep(duration)
            self.blocked_ips.discard(ip_address)
        
        threading.Thread(target=unblock, daemon=True).start()
        logger.warning(f"IP {ip_address} blocked for {duration} seconds")
    
    def mark_suspicious(self, ip_address: str):
        """Mark IP as suspicious"""
        self.suspicious_ips[ip_address] += 1
        
        # Auto-block after 5 suspicious activities
        if self.suspicious_ips[ip_address] >= 5:
            self.block_ip(ip_address, 7200)  # Block for 2 hours
            logger.warning(f"IP {ip_address} auto-blocked due to suspicious activity")
    
    def is_allowed(self, identifier: str, limit_type: str = 'general', custom_limit: Optional[Dict] = None) -> Tuple[bool, Dict]:
        """Enhanced rate limiting with IP blocking"""
        # Extract IP from identifier
        ip_address = identifier.split(':')[-1] if ':' in identifier else identifier
        
        # Check if IP is blocked
        if self.is_ip_blocked(ip_address):
            return False, {
                'limit': 0,
                'remaining': 0,
                'reset_time': int(time.time() + 3600),
                'retry_after': 3600,
                'blocked': True
            }
        
        # Whitelisted IPs bypass rate limiting
        if self.is_ip_whitelisted(ip_address):
            return True, {
                'limit': float('inf'),
                'remaining': float('inf'),
                'reset_time': 0,
                'retry_after': 0,
                'whitelisted': True
            }
        
        # Apply stricter limits for suspicious IPs
        if ip_address in self.suspicious_ips:
            if custom_limit:
                custom_limit['requests'] = max(1, custom_limit['requests'] // 2)
            else:
                limit_config = self.limits.get(limit_type, self.limits['general'])
                custom_limit = {
                    'requests': max(1, limit_config['requests'] // 2),
                    'window': limit_config['window']
                }
        
        is_allowed, result = super().is_allowed(identifier, limit_type, custom_limit)
        
        # Mark as suspicious if rate limit exceeded
        if not is_allowed:
            self.mark_suspicious(ip_address)
        
        return is_allowed, result

# Global rate limiter instance
rate_limiter = AdvancedRateLimiter()

# Rate limiting decorators
def rate_limit(limit_type: str = 'general', custom_limit: Optional[Dict] = None):
    """Rate limiting decorator"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            identifier = rate_limiter.get_client_identifier(request)
            is_allowed, limit_info = rate_limiter.is_allowed(identifier, limit_type, custom_limit)
            
            if not is_allowed:
                response = jsonify({
                    'error': 'Rate limit exceeded',
                    'limit': limit_info['limit'],
                    'remaining': limit_info['remaining'],
                    'reset_time': limit_info['reset_time'],
                    'retry_after': limit_info['retry_after']
                })
                response.status_code = 429
                response.headers['Retry-After'] = str(limit_info['retry_after'])
                response.headers['X-RateLimit-Limit'] = str(limit_info['limit'])
                response.headers['X-RateLimit-Remaining'] = str(limit_info['remaining'])
                response.headers['X-RateLimit-Reset'] = str(limit_info['reset_time'])
                return response
            
            # Add rate limit headers to successful responses
            response = f(*args, **kwargs)
            if hasattr(response, 'headers'):
                response.headers['X-RateLimit-Limit'] = str(limit_info['limit'])
                response.headers['X-RateLimit-Remaining'] = str(limit_info['remaining'])
                response.headers['X-RateLimit-Reset'] = str(limit_info['reset_time'])
            
            return response
        
        return decorated_function
    return decorator

def strict_rate_limit(requests: int, window: int):
    """Strict rate limiting decorator"""
    return rate_limit(custom_limit={'requests': requests, 'window': window})

def login_rate_limit(f):
    """Rate limiting for login attempts"""
    return rate_limit('login')(f)

def register_rate_limit(f):
    """Rate limiting for registration attempts"""
    return rate_limit('register')(f)

def api_rate_limit(f):
    """Rate limiting for API endpoints"""
    return rate_limit('api')(f)

def upload_rate_limit(f):
    """Rate limiting for file uploads"""
    return rate_limit('upload')(f)

def quiz_submit_rate_limit(f):
    """Rate limiting for quiz submissions"""
    return rate_limit('quiz_submit')(f)

# DDoS Protection
class DDoSProtection:
    """DDoS protection with advanced detection"""
    
    def __init__(self):
        self.request_counts = defaultdict(int)
        self.last_cleanup = time.time()
        self.cleanup_interval = 60  # Cleanup every minute
    
    def is_ddos_attack(self, ip_address: str, threshold: int = 100) -> bool:
        """Detect potential DDoS attack"""
        current_time = time.time()
        
        # Cleanup old data
        if current_time - self.last_cleanup > self.cleanup_interval:
            self._cleanup_old_data()
            self.last_cleanup = current_time
        
        # Count requests from this IP
        self.request_counts[ip_address] += 1
        
        # Check if threshold exceeded
        if self.request_counts[ip_address] > threshold:
            logger.warning(f"Potential DDoS attack detected from IP: {ip_address}")
            return True
        
        return False
    
    def _cleanup_old_data(self):
        """Clean up old request counts"""
        # Reset all counts (simple cleanup for testing)
        # In production, use time-based cleanup
        self.request_counts.clear()

# Global DDoS protection instance
ddos_protection = DDoSProtection()

def ddos_protection_decorator(threshold: int = 100):
    """DDoS protection decorator"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            ip_address = request.remote_addr
            
            if ddos_protection.is_ddos_attack(ip_address, threshold):
                return jsonify({'error': 'Too many requests'}), 429
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Rate limiting middleware
def rate_limiting_middleware(app):
    """Add rate limiting middleware to Flask app"""
    
    @app.before_request
    def before_request():
        # Skip rate limiting for health checks and static files
        if request.endpoint in ['health_check', 'static']:
            return
        
        # Apply general rate limiting
        identifier = rate_limiter.get_client_identifier(request)
        is_allowed, limit_info = rate_limiter.is_allowed(identifier, 'general')
        
        if not is_allowed:
            response = jsonify({
                'error': 'Rate limit exceeded',
                'retry_after': limit_info['retry_after']
            })
            response.status_code = 429
            response.headers['Retry-After'] = str(limit_info['retry_after'])
            return response
    
    @app.after_request
    def after_request(response):
        # Add rate limit headers to all responses
        identifier = rate_limiter.get_client_identifier(request)
        _, limit_info = rate_limiter.is_allowed(identifier, 'general')
        
        response.headers['X-RateLimit-Limit'] = str(limit_info['limit'])
        response.headers['X-RateLimit-Remaining'] = str(limit_info['remaining'])
        response.headers['X-RateLimit-Reset'] = str(limit_info['reset_time'])
        
        return response
