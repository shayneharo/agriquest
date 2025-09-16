"""
Caching Configuration and Management
Redis-based caching layer for improved performance
"""

import os
import json
import pickle
import hashlib
import logging
from functools import wraps
from typing import Any, Optional, Union, Callable
from datetime import timedelta

# Configure logging
logger = logging.getLogger(__name__)

class CacheManager:
    """Redis-based cache manager with fallback to memory cache"""
    
    def __init__(self):
        self.redis_client = None
        self.memory_cache = {}
        self._init_redis()
    
    def _init_redis(self):
        """Initialize Redis connection"""
        try:
            import redis
            redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
            
            # Test connection
            self.redis_client.ping()
            logger.info("Redis cache initialized successfully")
            
        except ImportError:
            logger.warning("Redis not available, using memory cache")
            self.redis_client = None
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}, using memory cache")
            self.redis_client = None
    
    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate cache key from arguments"""
        key_data = f"{prefix}:{str(args)}:{str(sorted(kwargs.items()))}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            if self.redis_client:
                value = self.redis_client.get(key)
                if value:
                    return json.loads(value)
            else:
                # Fallback to memory cache
                if key in self.memory_cache:
                    return self.memory_cache[key]
        except Exception as e:
            logger.error(f"Cache get error: {e}")
        
        return None
    
    def set(self, key: str, value: Any, expiration: int = 300) -> bool:
        """Set value in cache with expiration"""
        try:
            if self.redis_client:
                serialized_value = json.dumps(value, default=str)
                return self.redis_client.setex(key, expiration, serialized_value)
            else:
                # Fallback to memory cache
                self.memory_cache[key] = value
                return True
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete value from cache"""
        try:
            if self.redis_client:
                return bool(self.redis_client.delete(key))
            else:
                # Fallback to memory cache
                if key in self.memory_cache:
                    del self.memory_cache[key]
                    return True
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
        
        return False
    
    def clear(self, pattern: str = None) -> int:
        """Clear cache entries matching pattern"""
        try:
            if self.redis_client:
                if pattern:
                    keys = self.redis_client.keys(pattern)
                    if keys:
                        return self.redis_client.delete(*keys)
                else:
                    return self.redis_client.flushdb()
            else:
                # Fallback to memory cache
                if pattern:
                    keys_to_delete = [key for key in self.memory_cache.keys() if pattern in key]
                    for key in keys_to_delete:
                        del self.memory_cache[key]
                    return len(keys_to_delete)
                else:
                    self.memory_cache.clear()
                    return 0
        except Exception as e:
            logger.error(f"Cache clear error: {e}")
        
        return 0
    
    def get_or_set(self, key: str, func: Callable, expiration: int = 300, *args, **kwargs) -> Any:
        """Get value from cache or set it using function"""
        value = self.get(key)
        if value is None:
            value = func(*args, **kwargs)
            self.set(key, value, expiration)
        return value
    
    def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate cache entries matching pattern"""
        return self.clear(pattern)

# Global cache manager instance
cache_manager = CacheManager()

def cached(expiration: int = 300, key_prefix: str = None):
    """Decorator for caching function results"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            prefix = key_prefix or func.__name__
            cache_key = cache_manager._generate_key(prefix, *args, **kwargs)
            
            # Try to get from cache
            result = cache_manager.get(cache_key)
            if result is not None:
                logger.debug(f"Cache hit for {func.__name__}")
                return result
            
            # Execute function and cache result
            logger.debug(f"Cache miss for {func.__name__}")
            result = func(*args, **kwargs)
            cache_manager.set(cache_key, result, expiration)
            return result
        
        return wrapper
    return decorator

def cache_invalidate(pattern: str):
    """Decorator to invalidate cache after function execution"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            cache_manager.invalidate_pattern(pattern)
            logger.debug(f"Cache invalidated for pattern: {pattern}")
            return result
        return wrapper
    return decorator

# Specific cache decorators for different data types
def cache_user_data(expiration: int = 600):
    """Cache user-related data"""
    return cached(expiration=expiration, key_prefix='user')

def cache_quiz_data(expiration: int = 300):
    """Cache quiz-related data"""
    return cached(expiration=expiration, key_prefix='quiz')

def cache_analytics_data(expiration: int = 1800):
    """Cache analytics data (longer expiration)"""
    return cached(expiration=expiration, key_prefix='analytics')

def cache_subject_data(expiration: int = 3600):
    """Cache subject data (rarely changes)"""
    return cached(expiration=expiration, key_prefix='subject')

# Cache invalidation patterns
def invalidate_user_cache(user_id: int):
    """Invalidate all cache entries for a specific user"""
    patterns = [
        f'user:*{user_id}*',
        f'analytics:*{user_id}*',
        f'quiz:*{user_id}*'
    ]
    
    for pattern in patterns:
        cache_manager.invalidate_pattern(pattern)

def invalidate_quiz_cache(quiz_id: int):
    """Invalidate all cache entries for a specific quiz"""
    patterns = [
        f'quiz:*{quiz_id}*',
        f'analytics:*{quiz_id}*'
    ]
    
    for pattern in patterns:
        cache_manager.invalidate_pattern(pattern)

def invalidate_subject_cache(subject_id: int):
    """Invalidate all cache entries for a specific subject"""
    patterns = [
        f'subject:*{subject_id}*',
        f'quiz:*{subject_id}*'
    ]
    
    for pattern in patterns:
        cache_manager.invalidate_pattern(pattern)

# Session cache management
class SessionCache:
    """Session data caching"""
    
    @staticmethod
    def set_session(session_id: str, data: dict, expiration: int = 3600):
        """Store session data in cache"""
        key = f"session:{session_id}"
        cache_manager.set(key, data, expiration)
    
    @staticmethod
    def get_session(session_id: str) -> Optional[dict]:
        """Get session data from cache"""
        key = f"session:{session_id}"
        return cache_manager.get(key)
    
    @staticmethod
    def delete_session(session_id: str):
        """Delete session data from cache"""
        key = f"session:{session_id}"
        cache_manager.delete(key)
    
    @staticmethod
    def update_session(session_id: str, data: dict, expiration: int = 3600):
        """Update session data in cache"""
        existing_data = SessionCache.get_session(session_id) or {}
        existing_data.update(data)
        SessionCache.set_session(session_id, existing_data, expiration)

# Query result caching
class QueryCache:
    """Database query result caching"""
    
    @staticmethod
    def cache_query_result(query_hash: str, result: Any, expiration: int = 300):
        """Cache database query result"""
        key = f"query:{query_hash}"
        cache_manager.set(key, result, expiration)
    
    @staticmethod
    def get_cached_query_result(query_hash: str) -> Optional[Any]:
        """Get cached database query result"""
        key = f"query:{query_hash}"
        return cache_manager.get(key)
    
    @staticmethod
    def invalidate_query_cache(table_name: str):
        """Invalidate cache for queries involving specific table"""
        pattern = f"query:*{table_name}*"
        cache_manager.invalidate_pattern(pattern)

# Performance monitoring
class CacheStats:
    """Cache performance statistics"""
    
    def __init__(self):
        self.hits = 0
        self.misses = 0
        self.sets = 0
        self.deletes = 0
    
    def record_hit(self):
        self.hits += 1
    
    def record_miss(self):
        self.misses += 1
    
    def record_set(self):
        self.sets += 1
    
    def record_delete(self):
        self.deletes += 1
    
    def get_hit_rate(self) -> float:
        total = self.hits + self.misses
        return (self.hits / total * 100) if total > 0 else 0
    
    def get_stats(self) -> dict:
        return {
            'hits': self.hits,
            'misses': self.misses,
            'sets': self.sets,
            'deletes': self.deletes,
            'hit_rate': self.get_hit_rate()
        }

# Global cache statistics
cache_stats = CacheStats()

# Enhanced cache manager with statistics
class EnhancedCacheManager(CacheManager):
    """Enhanced cache manager with performance statistics"""
    
    def get(self, key: str) -> Optional[Any]:
        result = super().get(key)
        if result is not None:
            cache_stats.record_hit()
        else:
            cache_stats.record_miss()
        return result
    
    def set(self, key: str, value: Any, expiration: int = 300) -> bool:
        result = super().set(key, value, expiration)
        if result:
            cache_stats.record_set()
        return result
    
    def delete(self, key: str) -> bool:
        result = super().delete(key)
        if result:
            cache_stats.record_delete()
        return result

# Replace global cache manager with enhanced version
cache_manager = EnhancedCacheManager()

