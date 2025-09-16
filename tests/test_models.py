"""
Model Tests
Unit tests for all data models
"""

import pytest
from datetime import datetime
from backend.models.user import User
from backend.models.quiz import Quiz
from backend.models.class_model import Class
from backend.models.subject import Subject
from backend.models.result import Result

class TestUserModel:
    """Test User model functionality"""
    
    def test_create_user(self, db, sample_user):
        """Test user creation"""
        result = User.create_user(
            username=sample_user['username'],
            password=sample_user['password'],
            role=sample_user['role'],
            email=sample_user['email'],
            phone=sample_user['phone']
        )
        assert result is True
    
    def test_create_duplicate_user(self, db, sample_user):
        """Test duplicate user creation fails"""
        User.create_user(
            username=sample_user['username'],
            password=sample_user['password'],
            role=sample_user['role']
        )
        
        result = User.create_user(
            username=sample_user['username'],
            password=sample_user['password'],
            role=sample_user['role']
        )
        assert result is False
    
    def test_get_user_by_username(self, db, sample_user):
        """Test getting user by username"""
        User.create_user(
            username=sample_user['username'],
            password=sample_user['password'],
            role=sample_user['role']
        )
        
        user = User.get_user_by_username(sample_user['username'])
        assert user is not None
        assert user['username'] == sample_user['username']
        assert user['role'] == sample_user['role']
    
    def test_get_user_by_id(self, db, sample_user):
        """Test getting user by ID"""
        User.create_user(
            username=sample_user['username'],
            password=sample_user['password'],
            role=sample_user['role']
        )
        
        user = User.get_user_by_username(sample_user['username'])
        user_by_id = User.get_user_by_id(user['id'])
        
        assert user_by_id is not None
        assert user_by_id['username'] == sample_user['username']
    
    def test_update_user_role(self, db, sample_user):
        """Test updating user role"""
        User.create_user(
            username=sample_user['username'],
            password=sample_user['password'],
            role=sample_user['role']
        )
        
        user = User.get_user_by_username(sample_user['username'])
        User.update_user_role(user['id'], 'teacher')
        
        updated_user = User.get_user_by_id(user['id'])
        assert updated_user['role'] == 'teacher'
    
    def test_user_performance(self, db, sample_user):
        """Test user performance calculation"""
        User.create_user(
            username=sample_user['username'],
            password=sample_user['password'],
            role=sample_user['role']
        )
        
        user = User.get_user_by_username(sample_user['username'])
        performance = User.get_user_performance(user['id'])
        
        assert performance is not None
        assert 'total_quizzes' in performance
        assert 'avg_score' in performance
        assert 'pass_rate' in performance

class TestQuizModel:
    """Test Quiz model functionality"""
    
    def test_create_quiz(self, db, sample_quiz):
        """Test quiz creation"""
        # Create a subject first
        from backend.models.subject import Subject
        Subject.create_subject('Test Subject', 'Test description', 1)
        
        quiz_id = Quiz.create_quiz(
            title=sample_quiz['title'],
            subject_id=sample_quiz['subject_id'],
            creator_id=1,
            description=sample_quiz['description'],
            difficulty_level=sample_quiz['difficulty_level'],
            time_limit=sample_quiz['time_limit']
        )
        
        assert quiz_id is not None
        assert isinstance(quiz_id, int)
    
    def test_add_question(self, db, sample_quiz, sample_question):
        """Test adding question to quiz"""
        # Create quiz first
        from backend.models.subject import Subject
        Subject.create_subject('Test Subject', 'Test description', 1)
        
        quiz_id = Quiz.create_quiz(
            title=sample_quiz['title'],
            subject_id=sample_quiz['subject_id'],
            creator_id=1
        )
        
        # Add question
        Quiz.add_question(
            quiz_id=quiz_id,
            question_text=sample_question['question_text'],
            options=[
                sample_question['option1'],
                sample_question['option2'],
                sample_question['option3'],
                sample_question['option4']
            ],
            correct_option=sample_question['correct_option'],
            explanation=sample_question['explanation']
        )
        
        # Verify question was added
        questions = Quiz.get_questions_by_quiz_id(quiz_id)
        assert len(questions) == 1
        assert questions[0]['question_text'] == sample_question['question_text']
    
    def test_get_quiz_with_questions(self, db, sample_quiz, sample_question):
        """Test getting quiz with questions"""
        # Create quiz and question
        from backend.models.subject import Subject
        Subject.create_subject('Test Subject', 'Test description', 1)
        
        quiz_id = Quiz.create_quiz(
            title=sample_quiz['title'],
            subject_id=sample_quiz['subject_id'],
            creator_id=1
        )
        
        Quiz.add_question(
            quiz_id=quiz_id,
            question_text=sample_question['question_text'],
            options=[
                sample_question['option1'],
                sample_question['option2'],
                sample_question['option3'],
                sample_question['option4']
            ],
            correct_option=sample_question['correct_option']
        )
        
        quiz, questions = Quiz.get_quiz_with_questions(quiz_id)
        
        assert quiz is not None
        assert len(questions) == 1
        assert quiz['title'] == sample_quiz['title']
    
    def test_update_quiz(self, db, sample_quiz):
        """Test updating quiz"""
        from backend.models.subject import Subject
        Subject.create_subject('Test Subject', 'Test description', 1)
        
        quiz_id = Quiz.create_quiz(
            title=sample_quiz['title'],
            subject_id=sample_quiz['subject_id'],
            creator_id=1
        )
        
        # Update quiz
        Quiz.update_quiz(
            quiz_id=quiz_id,
            title='Updated Quiz Title',
            description='Updated description',
            difficulty_level='intermediate',
            time_limit=45
        )
        
        updated_quiz = Quiz.get_quiz_by_id(quiz_id)
        assert updated_quiz['title'] == 'Updated Quiz Title'
        assert updated_quiz['difficulty_level'] == 'intermediate'
        assert updated_quiz['time_limit'] == 45
    
    def test_delete_quiz(self, db, sample_quiz, sample_question):
        """Test deleting quiz"""
        from backend.models.subject import Subject
        Subject.create_subject('Test Subject', 'Test description', 1)
        
        quiz_id = Quiz.create_quiz(
            title=sample_quiz['title'],
            subject_id=sample_quiz['subject_id'],
            creator_id=1
        )
        
        # Add question
        Quiz.add_question(
            quiz_id=quiz_id,
            question_text=sample_question['question_text'],
            options=[
                sample_question['option1'],
                sample_question['option2'],
                sample_question['option3'],
                sample_question['option4']
            ],
            correct_option=sample_question['correct_option']
        )
        
        # Delete quiz
        Quiz.delete_quiz(quiz_id)
        
        # Verify quiz and questions are deleted
        quiz = Quiz.get_quiz_by_id(quiz_id)
        questions = Quiz.get_questions_by_quiz_id(quiz_id)
        
        assert quiz is None
        assert len(questions) == 0

class TestClassModel:
    """Test Class model functionality"""
    
    def test_get_all_classes(self, db):
        """Test getting all classes"""
        classes = Class.get_all_classes()
        assert isinstance(classes, list)
    
    def test_enroll_student(self, db, sample_user):
        """Test student enrollment"""
        # Create user and class
        User.create_user(
            username=sample_user['username'],
            password=sample_user['password'],
            role=sample_user['role']
        )
        
        user = User.get_user_by_username(sample_user['username'])
        
        # Create a class (assuming default classes exist)
        classes = Class.get_all_classes()
        if classes:
            class_id = classes[0]['id']
            
            result = Class.enroll_student(user['id'], class_id)
            assert result is True
            
            # Check enrollment status
            status = Class.get_student_enrollment_status(user['id'], class_id)
            assert status is not None
            assert status['status'] == 'pending'
    
    def test_approve_student(self, db, sample_user):
        """Test student approval"""
        # Create user and enroll in class
        User.create_user(
            username=sample_user['username'],
            password=sample_user['password'],
            role=sample_user['role']
        )
        
        user = User.get_user_by_username(sample_user['username'])
        classes = Class.get_all_classes()
        
        if classes:
            class_id = classes[0]['id']
            Class.enroll_student(user['id'], class_id)
            
            # Approve student
            result = Class.approve_student(user['id'], class_id)
            assert result is True
            
            # Check status
            status = Class.get_student_enrollment_status(user['id'], class_id)
            assert status['status'] == 'approved'
    
    def test_get_classes_for_student(self, db, sample_user):
        """Test getting classes for student"""
        User.create_user(
            username=sample_user['username'],
            password=sample_user['password'],
            role=sample_user['role']
        )
        
        user = User.get_user_by_username(sample_user['username'])
        classes = Class.get_classes_for_student(user['id'])
        
        assert isinstance(classes, list)

class TestSubjectModel:
    """Test Subject model functionality"""
    
    def test_create_subject(self, db):
        """Test subject creation"""
        from backend.models.subject import Subject
        
        result = Subject.create_subject(
            name='Test Subject',
            description='Test description',
            created_by=1
        )
        assert result is True
    
    def test_get_all_subjects(self, db):
        """Test getting all subjects"""
        from backend.models.subject import Subject
        
        subjects = Subject.get_all_subjects()
        assert isinstance(subjects, list)
    
    def test_get_subject_by_id(self, db):
        """Test getting subject by ID"""
        from backend.models.subject import Subject
        
        Subject.create_subject('Test Subject', 'Test description', 1)
        subjects = Subject.get_all_subjects()
        
        if subjects:
            subject = Subject.get_subject_by_id(subjects[0]['id'])
            assert subject is not None
            assert subject['name'] == 'Test Subject'

class TestResultModel:
    """Test Result model functionality"""
    
    def test_save_result(self, db, sample_user, sample_quiz, sample_question):
        """Test saving quiz result"""
        from backend.models.result import Result
        
        # Create user, subject, quiz, and question
        User.create_user(
            username=sample_user['username'],
            password=sample_user['password'],
            role=sample_user['role']
        )
        
        user = User.get_user_by_username(sample_user['username'])
        
        from backend.models.subject import Subject
        Subject.create_subject('Test Subject', 'Test description', 1)
        
        quiz_id = Quiz.create_quiz(
            title=sample_quiz['title'],
            subject_id=sample_quiz['subject_id'],
            creator_id=1
        )
        
        Quiz.add_question(
            quiz_id=quiz_id,
            question_text=sample_question['question_text'],
            options=[
                sample_question['option1'],
                sample_question['option2'],
                sample_question['option3'],
                sample_question['option4']
            ],
            correct_option=sample_question['correct_option']
        )
        
        # Save result
        result_id = Result.save_result(
            user_id=user['id'],
            quiz_id=quiz_id,
            score=1,
            total_questions=1
        )
        
        assert result_id is not None
    
    def test_get_user_results(self, db, sample_user):
        """Test getting user results"""
        from backend.models.result import Result
        
        User.create_user(
            username=sample_user['username'],
            password=sample_user['password'],
            role=sample_user['role']
        )
        
        user = User.get_user_by_username(sample_user['username'])
        results = Result.get_user_results(user['id'])
        
        assert isinstance(results, list)
    
    def test_get_quiz_results(self, db, sample_quiz):
        """Test getting quiz results"""
        from backend.models.result import Result
        
        from backend.models.subject import Subject
        Subject.create_subject('Test Subject', 'Test description', 1)
        
        quiz_id = Quiz.create_quiz(
            title=sample_quiz['title'],
            subject_id=sample_quiz['subject_id'],
            creator_id=1
        )
        
        results = Result.get_quiz_results(quiz_id)
        assert isinstance(results, list)

