"""
Optimized Database Configuration
Enhanced database management with connection pooling and performance monitoring
"""

import os
import sqlite3
import logging
from contextlib import contextmanager
from functools import wraps
import time
from typing import Optional, Dict, Any, List
from werkzeug.security import generate_password_hash

# Configure logging
logger = logging.getLogger(__name__)

class DatabaseManager:
    """Enhanced database manager with connection pooling and monitoring"""
    
    def __init__(self, database_url: str = None):
        self.database_url = database_url or os.getenv('DATABASE_URL', 'sqlite:///agriquest.db')
        self.connection_pool = {}
        self.query_stats = {}
        self._init_database()
    
    def _init_database(self):
        """Initialize database with optimized schema"""
        with self.get_connection() as conn:
            self._create_tables(conn)
            self._create_indexes(conn)
            self._seed_default_data(conn)
    
    @contextmanager
    def get_connection(self):
        """Get database connection with automatic cleanup"""
        conn = None
        try:
            if self.database_url.startswith('sqlite'):
                conn = sqlite3.connect(self.database_url.replace('sqlite:///', ''))
                conn.row_factory = sqlite3.Row
                conn.execute('PRAGMA foreign_keys = ON')
                conn.execute('PRAGMA journal_mode = WAL')
                conn.execute('PRAGMA synchronous = NORMAL')
                conn.execute('PRAGMA cache_size = 10000')
                conn.execute('PRAGMA temp_store = MEMORY')
            else:
                # PostgreSQL connection (for future migration)
                import psycopg2
                conn = psycopg2.connect(self.database_url)
                conn.autocommit = False
            
            yield conn
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def _create_tables(self, conn):
        """Create optimized database tables"""
        cursor = conn.cursor()
        
        # Users table with enhanced fields
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username VARCHAR(50) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                role VARCHAR(20) NOT NULL DEFAULT 'student',
                email VARCHAR(255) UNIQUE,
                phone VARCHAR(20),
                full_name VARCHAR(100),
                profile_picture VARCHAR(255),
                is_active BOOLEAN DEFAULT TRUE,
                email_verified BOOLEAN DEFAULT FALSE,
                phone_verified BOOLEAN DEFAULT FALSE,
                last_login TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Subjects table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS subjects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) UNIQUE NOT NULL,
                description TEXT,
                created_by INTEGER,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (created_by) REFERENCES users (id)
            )
        ''')
        
        # Quizzes table with enhanced fields
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS quizzes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title VARCHAR(200) NOT NULL,
                subject_id INTEGER,
                creator_id INTEGER,
                description TEXT,
                difficulty_level VARCHAR(20) DEFAULT 'beginner',
                time_limit INTEGER DEFAULT 0,
                is_published BOOLEAN DEFAULT FALSE,
                total_attempts INTEGER DEFAULT 0,
                average_score DECIMAL(5,2) DEFAULT 0.00,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (subject_id) REFERENCES subjects (id),
                FOREIGN KEY (creator_id) REFERENCES users (id)
            )
        ''')
        
        # Questions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                quiz_id INTEGER,
                question_text TEXT NOT NULL,
                option1 TEXT NOT NULL,
                option2 TEXT NOT NULL,
                option3 TEXT NOT NULL,
                option4 TEXT NOT NULL,
                correct_option INTEGER NOT NULL,
                explanation TEXT,
                difficulty_score INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (quiz_id) REFERENCES quizzes (id)
            )
        ''')
        
        # Results table with enhanced tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                quiz_id INTEGER,
                score INTEGER NOT NULL,
                total_questions INTEGER NOT NULL,
                percentage DECIMAL(5,2) NOT NULL,
                time_taken INTEGER DEFAULT 0,
                completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (quiz_id) REFERENCES quizzes (id)
            )
        ''')
        
        # Classes table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS classes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) NOT NULL,
                description TEXT,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Teacher classes junction table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS teacher_classes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                teacher_id INTEGER,
                class_id INTEGER,
                assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (teacher_id) REFERENCES users (id),
                FOREIGN KEY (class_id) REFERENCES classes (id),
                UNIQUE(teacher_id, class_id)
            )
        ''')
        
        # Student classes junction table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS student_classes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER,
                class_id INTEGER,
                status VARCHAR(20) DEFAULT 'pending',
                requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                approved_at TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES users (id),
                FOREIGN KEY (class_id) REFERENCES classes (id),
                UNIQUE(student_id, class_id)
            )
        ''')
        
        # OTP codes table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS otp_codes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                code VARCHAR(10) NOT NULL,
                type VARCHAR(20) NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                is_used BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # User sessions table for enhanced session management
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                session_id VARCHAR(255) UNIQUE NOT NULL,
                ip_address VARCHAR(45),
                user_agent TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Performance analytics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance_analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                quiz_id INTEGER,
                question_id INTEGER,
                response_time INTEGER,
                is_correct BOOLEAN,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (quiz_id) REFERENCES quizzes (id),
                FOREIGN KEY (question_id) REFERENCES questions (id)
            )
        ''')
    
    def _create_indexes(self, conn):
        """Create performance indexes"""
        cursor = conn.cursor()
        
        # User indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_role ON users(role)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_active ON users(is_active)')
        
        # Quiz indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_quizzes_subject_id ON quizzes(subject_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_quizzes_creator_id ON quizzes(creator_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_quizzes_published ON quizzes(is_published)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_quizzes_created_at ON quizzes(created_at)')
        
        # Question indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_questions_quiz_id ON questions(quiz_id)')
        
        # Result indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_results_user_id ON results(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_results_quiz_id ON results(quiz_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_results_completed_at ON results(completed_at)')
        
        # Class indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_teacher_classes_teacher_id ON teacher_classes(teacher_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_teacher_classes_class_id ON teacher_classes(class_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_student_classes_student_id ON student_classes(student_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_student_classes_class_id ON student_classes(class_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_student_classes_status ON student_classes(status)')
        
        # OTP indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_otp_codes_user_id ON otp_codes(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_otp_codes_expires_at ON otp_codes(expires_at)')
        
        # Session indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_sessions_session_id ON user_sessions(session_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_sessions_expires_at ON user_sessions(expires_at)')
        
        # Analytics indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_performance_user_id ON performance_analytics(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_performance_quiz_id ON performance_analytics(quiz_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_performance_created_at ON performance_analytics(created_at)')
    
    def _seed_default_data(self, conn):
        """Seed database with default data"""
        cursor = conn.cursor()
        
        # Check if data already exists
        cursor.execute('SELECT COUNT(*) FROM subjects')
        if cursor.fetchone()[0] > 0:
            return
        
        # Default subjects
        default_subjects = [
            ('Crop Science', 'Study of crop production, breeding, and management techniques for optimal yield and quality'),
            ('Soil Science', 'Understanding soil properties, fertility, composition, and sustainable soil management practices'),
            ('Crop Protection', 'Study of plant diseases, pests, weeds, and integrated pest management strategies'),
            ('Animal Science', 'Comprehensive study of animal nutrition, breeding, health, and production systems'),
            ('Agricultural Economics and Marketing', 'Economic principles, market analysis, and business strategies in agriculture'),
            ('Agricultural Extension and Communication', 'Methods of knowledge transfer, farmer education, and agricultural communication')
        ]
        
        for subject_name, description in default_subjects:
            cursor.execute(
                'INSERT INTO subjects (name, description, created_by) VALUES (?, ?, ?)',
                (subject_name, description, 1)
            )
        
        # Default admin user
        admin_password = generate_password_hash('Admin123!')
        cursor.execute('''
            INSERT OR IGNORE INTO users (id, username, password_hash, role, email, phone, full_name, is_active, email_verified, phone_verified)
            VALUES (1, 'admin', ?, 'admin', 'admin@agriquest.com', '+1234567890', 'System Administrator', TRUE, TRUE, TRUE)
        ''', (admin_password,))
        
        # Default test users
        test_users = [
            ('teacher', 'Teacher123!', 'teacher', 'teacher@agriquest.com', '+1234567890', 'Test Teacher'),
            ('student', 'Student123!', 'student', 'student@agriquest.com', '+1234567890', 'Test Student')
        ]
        
        for username, password, role, email, phone, full_name in test_users:
            password_hash = generate_password_hash(password)
            cursor.execute('''
                INSERT OR IGNORE INTO users (username, password_hash, role, email, phone, full_name, is_active, email_verified, phone_verified)
                VALUES (?, ?, ?, ?, ?, ?, TRUE, TRUE, TRUE)
            ''', (username, password_hash, role, email, phone, full_name))
        
        # Default classes
        default_classes = [
            ('Introduction to Agriculture', 'Basic concepts and principles of agriculture'),
            ('Advanced Crop Management', 'Advanced techniques in crop production and management'),
            ('Agricultural Technology', 'Modern technology applications in agriculture'),
            ('Sustainable Farming', 'Environmentally sustainable farming practices'),
            ('Agricultural Business', 'Business aspects of agricultural operations')
        ]
        
        for class_name, description in default_classes:
            cursor.execute(
                'INSERT INTO classes (name, description) VALUES (?, ?)',
                (class_name, description)
            )
    
    def execute_query(self, query: str, params: tuple = (), fetch: str = 'all') -> Any:
        """Execute database query with performance monitoring"""
        start_time = time.time()
        
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                
                if fetch == 'one':
                    result = cursor.fetchone()
                elif fetch == 'all':
                    result = cursor.fetchall()
                else:
                    result = cursor.rowcount
                
                # Log slow queries
                execution_time = time.time() - start_time
                if execution_time > 0.1:  # Log queries taking more than 100ms
                    logger.warning(f"Slow query ({execution_time:.3f}s): {query[:100]}...")
                
                # Update query statistics
                query_hash = hash(query)
                if query_hash not in self.query_stats:
                    self.query_stats[query_hash] = {
                        'query': query,
                        'count': 0,
                        'total_time': 0,
                        'avg_time': 0
                    }
                
                stats = self.query_stats[query_hash]
                stats['count'] += 1
                stats['total_time'] += execution_time
                stats['avg_time'] = stats['total_time'] / stats['count']
                
                return result
                
        except Exception as e:
            logger.error(f"Query execution error: {e}")
            raise
    
    def get_query_stats(self) -> Dict[str, Any]:
        """Get query performance statistics"""
        return self.query_stats
    
    def cleanup_expired_data(self):
        """Clean up expired OTP codes and sessions"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Clean expired OTP codes
            cursor.execute('DELETE FROM otp_codes WHERE expires_at < CURRENT_TIMESTAMP')
            otp_deleted = cursor.rowcount
            
            # Clean expired sessions
            cursor.execute('DELETE FROM user_sessions WHERE expires_at < CURRENT_TIMESTAMP')
            session_deleted = cursor.rowcount
            
            logger.info(f"Cleaned up {otp_deleted} expired OTP codes and {session_deleted} expired sessions")

# Global database manager instance
db_manager = DatabaseManager()

def get_db_connection():
    """Get database connection (backward compatibility)"""
    return db_manager.get_connection()

def init_db():
    """Initialize database (backward compatibility)"""
    # Database is automatically initialized when DatabaseManager is created
    pass

# Performance monitoring decorator
def monitor_performance(func):
    """Decorator to monitor function performance"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        execution_time = time.time() - start_time
        
        if execution_time > 0.1:  # Log slow operations
            logger.warning(f"Slow operation in {func.__name__}: {execution_time:.3f}s")
        
        return result
    return wrapper
