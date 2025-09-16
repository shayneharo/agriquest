"""
AgriQuest Testing Framework
Comprehensive testing suite for all components
"""

import os
import sys
import pytest
from unittest.mock import Mock, patch

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Test configuration
TEST_CONFIG = {
    'TESTING': True,
    'DATABASE_URL': 'sqlite:///:memory:',
    'SECRET_KEY': 'test-secret-key',
    'WTF_CSRF_ENABLED': False,
    'MAIL_SUPPRESS_SEND': True,
    'CACHE_TYPE': 'null'
}

# Test fixtures and utilities
@pytest.fixture
def app():
    """Create test application"""
    from backend import create_app
    app = create_app('testing')
    app.config.update(TEST_CONFIG)
    
    with app.app_context():
        yield app

@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()

@pytest.fixture
def db(app):
    """Create test database"""
    from backend.config.database_optimized import db_manager
    db_manager._init_database()
    yield db_manager
    # Cleanup after test

@pytest.fixture
def auth_headers():
    """Create authentication headers for testing"""
    return {
        'Authorization': 'Bearer test-token',
        'Content-Type': 'application/json'
    }

@pytest.fixture
def sample_user():
    """Create sample user data"""
    return {
        'username': 'testuser',
        'password': 'TestPassword123!',
        'email': 'test@example.com',
        'phone': '+1234567890',
        'role': 'student'
    }

@pytest.fixture
def sample_quiz():
    """Create sample quiz data"""
    return {
        'title': 'Test Quiz',
        'description': 'A test quiz',
        'subject_id': 1,
        'difficulty_level': 'beginner',
        'time_limit': 30
    }

@pytest.fixture
def sample_question():
    """Create sample question data"""
    return {
        'question_text': 'What is 2+2?',
        'option1': '3',
        'option2': '4',
        'option3': '5',
        'option4': '6',
        'correct_option': 2,
        'explanation': '2+2 equals 4'
    }

