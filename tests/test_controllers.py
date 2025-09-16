"""
Controller Tests
Integration tests for Flask routes and controllers
"""

import pytest
import json
from unittest.mock import patch, Mock
from backend.controllers.auth_controller import auth_bp
from backend.controllers.quiz_controller import quiz_bp
from backend.controllers.classes_controller import classes_bp

class TestAuthController:
    """Test authentication controller"""
    
    def test_register_page(self, client):
        """Test registration page loads"""
        response = client.get('/register')
        assert response.status_code == 200
        assert b'Join AgriQuest' in response.data
    
    def test_login_page(self, client):
        """Test login page loads"""
        response = client.get('/login')
        assert response.status_code == 200
        assert b'Welcome Back' in response.data
    
    def test_register_user(self, client, sample_user):
        """Test user registration"""
        with patch('backend.controllers.auth_controller.User.create_user') as mock_create:
            with patch('backend.controllers.auth_controller.send_otp') as mock_otp:
                mock_create.return_value = True
                mock_otp.return_value = True
                
                response = client.post('/register', data=sample_user)
                assert response.status_code == 200
                assert b'OTP Verification' in response.data
    
    def test_register_duplicate_user(self, client, sample_user):
        """Test registration with duplicate username"""
        with patch('backend.controllers.auth_controller.User.create_user') as mock_create:
            mock_create.return_value = False
            
            response = client.post('/register', data=sample_user)
            assert response.status_code == 200
            assert b'Username already exists' in response.data
    
    def test_login_valid_credentials(self, client, sample_user):
        """Test login with valid credentials"""
        with patch('backend.controllers.auth_controller.User.get_user_by_username') as mock_get_user:
            with patch('backend.controllers.auth_controller.check_password_hash') as mock_check:
                mock_get_user.return_value = {
                    'id': 1,
                    'username': sample_user['username'],
                    'password': 'hashed_password',
                    'role': sample_user['role']
                }
                mock_check.return_value = True
                
                response = client.post('/login', data={
                    'username': sample_user['username'],
                    'password': sample_user['password']
                })
                
                assert response.status_code == 302  # Redirect to dashboard
    
    def test_login_invalid_credentials(self, client, sample_user):
        """Test login with invalid credentials"""
        with patch('backend.controllers.auth_controller.User.get_user_by_username') as mock_get_user:
            with patch('backend.controllers.auth_controller.check_password_hash') as mock_check:
                mock_get_user.return_value = {
                    'id': 1,
                    'username': sample_user['username'],
                    'password': 'hashed_password',
                    'role': sample_user['role']
                }
                mock_check.return_value = False
                
                response = client.post('/login', data={
                    'username': sample_user['username'],
                    'password': 'wrong_password'
                })
                
                assert response.status_code == 200
                assert b'Invalid credentials' in response.data
    
    def test_logout(self, client):
        """Test user logout"""
        with client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['username'] = 'testuser'
            sess['role'] = 'student'
        
        response = client.post('/logout')
        assert response.status_code == 302  # Redirect to login
    
    def test_forgot_password(self, client):
        """Test forgot password functionality"""
        with patch('backend.controllers.auth_controller.User.get_user_by_email') as mock_get_user:
            with patch('backend.controllers.auth_controller.send_otp') as mock_otp:
                mock_get_user.return_value = {'id': 1, 'email': 'test@example.com'}
                mock_otp.return_value = True
                
                response = client.post('/forgot_password', data={
                    'email': 'test@example.com'
                })
                
                assert response.status_code == 200
                assert b'OTP sent' in response.data
    
    def test_reset_password(self, client):
        """Test password reset"""
        with patch('backend.controllers.auth_controller.verify_otp') as mock_verify:
            with patch('backend.controllers.auth_controller.User.update_password') as mock_update:
                mock_verify.return_value = True
                mock_update.return_value = True
                
                response = client.post('/reset_password', data={
                    'otp': '123456',
                    'new_password': 'NewPassword123!'
                })
                
                assert response.status_code == 200
                assert b'Password reset successfully' in response.data

class TestQuizController:
    """Test quiz controller"""
    
    def test_dashboard_student(self, client):
        """Test student dashboard"""
        with client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['username'] = 'student'
            sess['role'] = 'student'
        
        with patch('backend.controllers.quiz_controller.Quiz.get_all_quizzes') as mock_get_quizzes:
            mock_get_quizzes.return_value = []
            
            response = client.get('/')
            assert response.status_code == 200
            assert b'Student Dashboard' in response.data
    
    def test_dashboard_teacher(self, client):
        """Test teacher dashboard"""
        with client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['username'] = 'teacher'
            sess['role'] = 'teacher'
        
        with patch('backend.controllers.quiz_controller.User.get_teacher_quizzes') as mock_get_quizzes:
            mock_get_quizzes.return_value = []
            
            response = client.get('/')
            assert response.status_code == 200
            assert b'Teacher Dashboard' in response.data
    
    def test_create_quiz_page(self, client):
        """Test create quiz page"""
        with client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['username'] = 'teacher'
            sess['role'] = 'teacher'
        
        with patch('backend.controllers.quiz_controller.Subject.get_all_subjects') as mock_get_subjects:
            mock_get_subjects.return_value = []
            
            response = client.get('/create_quiz')
            assert response.status_code == 200
            assert b'Create New Quiz' in response.data
    
    def test_create_quiz(self, client, sample_quiz):
        """Test quiz creation"""
        with client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['username'] = 'teacher'
            sess['role'] = 'teacher'
        
        with patch('backend.controllers.quiz_controller.Quiz.create_quiz') as mock_create:
            mock_create.return_value = 1
            
            response = client.post('/create_quiz', data=sample_quiz)
            assert response.status_code == 302  # Redirect to add questions
    
    def test_take_quiz(self, client, sample_quiz, sample_question):
        """Test taking a quiz"""
        with client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['username'] = 'student'
            sess['role'] = 'student'
        
        with patch('backend.controllers.quiz_controller.Quiz.get_quiz_with_questions') as mock_get_quiz:
            mock_get_quiz.return_value = (
                {'id': 1, 'title': sample_quiz['title']},
                [{'id': 1, 'question_text': sample_question['question_text']}]
            )
            
            response = client.get('/quiz/1')
            assert response.status_code == 200
            assert b'Take Quiz' in response.data
    
    def test_submit_quiz(self, client):
        """Test quiz submission"""
        with client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['username'] = 'student'
            sess['role'] = 'student'
        
        with patch('backend.controllers.quiz_controller.Quiz.get_questions_by_quiz_id') as mock_get_questions:
            with patch('backend.controllers.quiz_controller.Result.save_result') as mock_save_result:
                mock_get_questions.return_value = [
                    {'id': 1, 'correct_option': 1}
                ]
                mock_save_result.return_value = 1
                
                response = client.post('/quiz/1/submit', data={
                    'question_1': '1'
                })
                
                assert response.status_code == 200
                assert b'Quiz Results' in response.data
    
    def test_edit_quiz(self, client, sample_quiz):
        """Test quiz editing"""
        with client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['username'] = 'teacher'
            sess['role'] = 'teacher'
        
        with patch('backend.controllers.quiz_controller.Quiz.get_quiz_by_id') as mock_get_quiz:
            with patch('backend.controllers.quiz_controller.Quiz.update_quiz') as mock_update:
                mock_get_quiz.return_value = {'id': 1, 'title': 'Old Title'}
                mock_update.return_value = True
                
                response = client.post('/edit_quiz/1', data={
                    'title': 'Updated Title',
                    'description': 'Updated description',
                    'difficulty_level': 'intermediate',
                    'time_limit': '45'
                })
                
                assert response.status_code == 302  # Redirect to quiz list
    
    def test_delete_quiz(self, client):
        """Test quiz deletion"""
        with client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['username'] = 'teacher'
            sess['role'] = 'teacher'
        
        with patch('backend.controllers.quiz_controller.Quiz.delete_quiz') as mock_delete:
            mock_delete.return_value = True
            
            response = client.post('/delete_quiz/1')
            assert response.status_code == 302  # Redirect to quiz list

class TestClassesController:
    """Test classes controller"""
    
    def test_classes_page(self, client):
        """Test classes page"""
        with client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['username'] = 'student'
            sess['role'] = 'student'
        
        with patch('backend.controllers.classes_controller.Class.get_all_classes') as mock_get_classes:
            with patch('backend.controllers.classes_controller.Class.get_student_enrollment_status') as mock_get_status:
                mock_get_classes.return_value = [
                    {'id': 1, 'name': 'Test Class', 'description': 'Test description'}
                ]
                mock_get_status.return_value = None
                
                response = client.get('/classes')
                assert response.status_code == 200
                assert b'Available Classes' in response.data
    
    def test_enroll_in_class(self, client):
        """Test class enrollment"""
        with client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['username'] = 'student'
            sess['role'] = 'student'
        
        with patch('backend.controllers.classes_controller.Class.enroll_student') as mock_enroll:
            mock_enroll.return_value = True
            
            response = client.post('/enroll/1')
            assert response.status_code == 302  # Redirect to classes page
    
    def test_my_classes(self, client):
        """Test my classes page"""
        with client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['username'] = 'student'
            sess['role'] = 'student'
        
        with patch('backend.controllers.classes_controller.Class.get_classes_for_student') as mock_get_classes:
            mock_get_classes.return_value = [
                {'id': 1, 'name': 'Test Class', 'status': 'approved'}
            ]
            
            response = client.get('/my_classes')
            assert response.status_code == 200
            assert b'My Classes' in response.data
    
    def test_manage_class_teacher(self, client):
        """Test class management for teachers"""
        with client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['username'] = 'teacher'
            sess['role'] = 'teacher'
        
        with patch('backend.controllers.classes_controller.Class.get_class_by_id') as mock_get_class:
            with patch('backend.controllers.classes_controller.Class.get_pending_enrollments_for_class') as mock_get_pending:
                with patch('backend.controllers.classes_controller.Class.is_teacher_of_class') as mock_is_teacher:
                    mock_get_class.return_value = {'id': 1, 'name': 'Test Class'}
                    mock_get_pending.return_value = []
                    mock_is_teacher.return_value = True
                    
                    response = client.get('/manage_class/1')
                    assert response.status_code == 200
                    assert b'Manage Class' in response.data
    
    def test_approve_enrollment(self, client):
        """Test enrollment approval"""
        with client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['username'] = 'teacher'
            sess['role'] = 'teacher'
        
        with patch('backend.controllers.classes_controller.Class.approve_student') as mock_approve:
            mock_approve.return_value = True
            
            response = client.post('/manage_enrollment/1/approve')
            assert response.status_code == 302  # Redirect to manage class
    
    def test_reject_enrollment(self, client):
        """Test enrollment rejection"""
        with client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['username'] = 'teacher'
            sess['role'] = 'teacher'
        
        with patch('backend.controllers.classes_controller.Class.reject_student') as mock_reject:
            mock_reject.return_value = True
            
            response = client.post('/manage_enrollment/1/reject')
            assert response.status_code == 302  # Redirect to manage class

class TestSecurityIntegration:
    """Test security integration in controllers"""
    
    def test_unauthorized_access(self, client):
        """Test unauthorized access to protected routes"""
        # Try to access dashboard without login
        response = client.get('/')
        assert response.status_code == 302  # Redirect to login
    
    def test_teacher_only_access(self, client):
        """Test teacher-only routes"""
        with client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['username'] = 'student'
            sess['role'] = 'student'
        
        # Student trying to access teacher route
        response = client.get('/create_quiz')
        assert response.status_code == 403  # Forbidden
    
    def test_csrf_protection(self, client):
        """Test CSRF protection"""
        with client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['username'] = 'teacher'
            sess['role'] = 'teacher'
        
        # Try to create quiz without CSRF token
        response = client.post('/create_quiz', data={
            'title': 'Test Quiz',
            'subject_id': '1'
        })
        assert response.status_code == 400  # Bad request due to CSRF
    
    def test_rate_limiting(self, client):
        """Test rate limiting on login"""
        # Make multiple login attempts
        for i in range(6):
            response = client.post('/login', data={
                'username': 'testuser',
                'password': 'wrongpassword'
            })
        
        # Should be rate limited
        assert response.status_code == 429  # Too many requests

class TestErrorHandling:
    """Test error handling in controllers"""
    
    def test_404_error(self, client):
        """Test 404 error handling"""
        response = client.get('/nonexistent-page')
        assert response.status_code == 404
    
    def test_500_error(self, client):
        """Test 500 error handling"""
        with patch('backend.controllers.quiz_controller.Quiz.get_all_quizzes') as mock_get_quizzes:
            mock_get_quizzes.side_effect = Exception('Database error')
            
            with client.session_transaction() as sess:
                sess['user_id'] = 1
                sess['username'] = 'student'
                sess['role'] = 'student'
            
            response = client.get('/')
            assert response.status_code == 500
    
    def test_database_connection_error(self, client):
        """Test database connection error handling"""
        with patch('backend.controllers.auth_controller.User.create_user') as mock_create:
            mock_create.side_effect = Exception('Database connection failed')
            
            response = client.post('/register', data={
                'username': 'testuser',
                'password': 'TestPassword123!',
                'role': 'student'
            })
            
            assert response.status_code == 500

