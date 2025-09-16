# database.py
import os
import sqlite3
from urllib.parse import urlparse
from werkzeug.security import generate_password_hash

# Optional PostgreSQL imports
try:
    import psycopg2
    from psycopg2.extras import DictCursor
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False

def get_db_connection():
    """Get database connection based on environment"""
    database_url = os.getenv('DATABASE_URL')
    
    if database_url and database_url.startswith('postgres://') and PSYCOPG2_AVAILABLE:
        # Parse the URL
        url = urlparse(database_url)
        
        # Connect to PostgreSQL
        conn = psycopg2.connect(
            database=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
        )
        conn.cursor_factory = DictCursor
        return conn
    else:
        # Fallback to SQLite for local development
        conn = sqlite3.connect('agriquest.db')
        conn.row_factory = sqlite3.Row
        return conn

def init_db():
    """Initialize the database with PostgreSQL compatible schema"""
    conn = get_db_connection()
    c = conn.cursor()
    
    # Determine if we're using PostgreSQL or SQLite
    is_postgres = PSYCOPG2_AVAILABLE and hasattr(conn, 'cursor_factory')
    
    # Define ID column type based on database
    id_type = "SERIAL" if is_postgres else "INTEGER"
    auto_timestamp = "TIMESTAMP DEFAULT CURRENT_TIMESTAMP" if is_postgres else "DATETIME DEFAULT CURRENT_TIMESTAMP"
    
    # Check if users table exists
    if not is_postgres:
        c.execute("PRAGMA table_info(users)")
    columns = [column[1] for column in c.fetchall()]
    
    # Users table
    create_users_table = f'''CREATE TABLE IF NOT EXISTS users
                 (id {id_type} PRIMARY KEY,
                  username VARCHAR(50) UNIQUE NOT NULL,
                  password VARCHAR(255) NOT NULL,
                  role VARCHAR(20) NOT NULL DEFAULT 'student',
                  email VARCHAR(255),
                  created_at {auto_timestamp})'''
    c.execute(create_users_table)
    
    # Add new columns if they don't exist
    if 'role' not in columns:
        c.execute("ALTER TABLE users ADD COLUMN role TEXT NOT NULL DEFAULT 'student'")
    if 'email' not in columns:
        c.execute("ALTER TABLE users ADD COLUMN email TEXT")
    if 'created_at' not in columns:
        c.execute("ALTER TABLE users ADD COLUMN created_at DATETIME")
        # Update existing records with current timestamp
        c.execute("UPDATE users SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL")
    
    # Subjects table
    create_subjects_table = f'''CREATE TABLE IF NOT EXISTS subjects
                 (id {id_type} PRIMARY KEY,
                  name VARCHAR(100) UNIQUE NOT NULL,
                  description TEXT,
                  created_by INTEGER REFERENCES users(id),
                  created_at {auto_timestamp})'''
    c.execute(create_subjects_table)
    
    # Check if quizzes table exists and has the new columns
    c.execute("PRAGMA table_info(quizzes)")
    quiz_columns = [column[1] for column in c.fetchall()]
    
    # Quizzes table
    create_quizzes_table = f'''CREATE TABLE IF NOT EXISTS quizzes
                 (id {id_type} PRIMARY KEY,
                  title VARCHAR(255) NOT NULL,
                  subject_id INTEGER REFERENCES subjects(id),
                  creator_id INTEGER REFERENCES users(id),
                  description TEXT,
                  difficulty_level VARCHAR(20) DEFAULT 'beginner',
                  time_limit INTEGER DEFAULT 0,
                  created_at {auto_timestamp})'''
    c.execute(create_quizzes_table)
    
    # Add new columns to quizzes table if they don't exist
    if 'subject_id' not in quiz_columns:
        c.execute("ALTER TABLE quizzes ADD COLUMN subject_id INTEGER")
    if 'description' not in quiz_columns:
        c.execute("ALTER TABLE quizzes ADD COLUMN description TEXT")
    if 'difficulty_level' not in quiz_columns:
        c.execute("ALTER TABLE quizzes ADD COLUMN difficulty_level TEXT DEFAULT 'beginner'")
    if 'time_limit' not in quiz_columns:
        c.execute("ALTER TABLE quizzes ADD COLUMN time_limit INTEGER DEFAULT 0")
    if 'created_at' not in quiz_columns:
        c.execute("ALTER TABLE quizzes ADD COLUMN created_at DATETIME")
        # Update existing records with current timestamp
        c.execute("UPDATE quizzes SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL")
    
    # Check if explanation column exists in questions table
    c.execute("PRAGMA table_info(questions)")
    question_columns = [column[1] for column in c.fetchall()]
    if 'explanation' not in question_columns:
        c.execute("ALTER TABLE questions ADD COLUMN explanation TEXT")
    
    # Questions table
    create_questions_table = f'''CREATE TABLE IF NOT EXISTS questions
                 (id {id_type} PRIMARY KEY,
                  quiz_id INTEGER REFERENCES quizzes(id),
                  question_text TEXT NOT NULL,
                  option1 TEXT NOT NULL,
                  option2 TEXT NOT NULL,
                  option3 TEXT NOT NULL,
                  option4 TEXT NOT NULL,
                  correct_option INTEGER NOT NULL,
                  explanation TEXT)'''
    c.execute(create_questions_table)
    
    # Results table
    create_results_table = f'''CREATE TABLE IF NOT EXISTS results
                 (id {id_type} PRIMARY KEY,
                  user_id INTEGER REFERENCES users(id),
                  quiz_id INTEGER REFERENCES quizzes(id),
                  score INTEGER NOT NULL,
                  total_questions INTEGER NOT NULL,
                  timestamp {auto_timestamp})'''
    c.execute(create_results_table)
    
    # Update existing admin users to teacher role
    c.execute("UPDATE users SET role = 'teacher' WHERE role = 'admin'")
    
    # Create default subjects
    default_subjects = [
        ('Crop Science', 'Study of crop production, breeding, and management techniques for optimal yield and quality'),
        ('Soil Science', 'Understanding soil properties, fertility, composition, and sustainable soil management practices'),
        ('Crop Protection', 'Study of plant diseases, pests, weeds, and integrated pest management strategies'),
        ('Animal Science', 'Comprehensive study of animal nutrition, breeding, health, and production systems'),
        ('Agricultural Economics and Marketing', 'Economic principles, market analysis, and business strategies in agriculture'),
        ('Agricultural Extension and Communication', 'Methods of knowledge transfer, farmer education, and agricultural communication')
    ]
    
    for subject_name, description in default_subjects:
        try:
            c.execute("INSERT INTO subjects (name, description, created_by) VALUES (?, ?, ?)", 
                     (subject_name, description, 1))  # Admin user ID
        except sqlite3.IntegrityError:
            pass  # Subject already exists
    
    conn.commit()
    conn.close()
    
    # Migrate OTP table if needed
    from ..utils.otp_utils import migrate_otp_table
    migrate_otp_table()

def get_db_connection():
    conn = sqlite3.connect('agriquest.db')
    conn.row_factory = sqlite3.Row
    return conn