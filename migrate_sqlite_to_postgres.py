#!/usr/bin/env python3
"""
SQLite to PostgreSQL Migration Script for AgriQuest

This script migrates your existing SQLite database to PostgreSQL for Render.com deployment.
It preserves all existing data and creates a PostgreSQL-compatible schema.

Usage:
    python migrate_sqlite_to_postgres.py

Requirements:
    pip install psycopg2-binary

Author: AgriQuest Development Team
Version: 2.0
"""

import sqlite3
import psycopg2
from psycopg2.extras import DictCursor
import os
import sys
from datetime import datetime
from urllib.parse import urlparse

def get_sqlite_connection():
    """Get SQLite connection"""
    return sqlite3.connect('agriquest.db')

def get_postgres_connection():
    """Get PostgreSQL connection from DATABASE_URL"""
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL environment variable not set")
        print("Please set your PostgreSQL connection string:")
        print("export DATABASE_URL='postgres://username:password@host:port/database'")
        sys.exit(1)
    
    url = urlparse(database_url)
    conn = psycopg2.connect(
        database=url.path[1:],
        user=url.username,
        password=url.password,
        host=url.hostname,
        port=url.port
    )
    conn.cursor_factory = DictCursor
    return conn

def create_postgres_schema(conn):
    """Create PostgreSQL schema"""
    cursor = conn.cursor()
    
    print("📝 Creating PostgreSQL schema...")
    
    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            role VARCHAR(20) NOT NULL CHECK (role IN ('admin', 'teacher', 'student')),
            email VARCHAR(100) UNIQUE NOT NULL,
            full_name VARCHAR(100),
            user_id VARCHAR(20) UNIQUE,
            is_active BOOLEAN DEFAULT TRUE,
            last_login TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Subjects table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS subjects (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_by INTEGER REFERENCES users(id)
        )
    """)
    
    # Quizzes table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS quizzes (
            id SERIAL PRIMARY KEY,
            title VARCHAR(200) NOT NULL,
            description TEXT,
            subject_id INTEGER REFERENCES subjects(id),
            created_by INTEGER REFERENCES users(id),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT TRUE
        )
    """)
    
    # Questions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS questions (
            id SERIAL PRIMARY KEY,
            quiz_id INTEGER REFERENCES quizzes(id),
            question_text TEXT NOT NULL,
            question_type VARCHAR(20) DEFAULT 'multiple_choice',
            options TEXT,
            correct_answer TEXT,
            points INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Results table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS results (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id),
            quiz_id INTEGER REFERENCES quizzes(id),
            score INTEGER,
            total_questions INTEGER,
            percentage DECIMAL(5,2),
            answers TEXT,
            completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Classes table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS classes (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            description TEXT,
            subject_id INTEGER REFERENCES subjects(id),
            created_by INTEGER REFERENCES users(id),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Teacher Classes table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS teacher_classes (
            id SERIAL PRIMARY KEY,
            teacher_id INTEGER REFERENCES users(id),
            class_id INTEGER REFERENCES classes(id),
            assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(teacher_id, class_id)
        )
    """)
    
    # Student Classes table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS student_classes (
            id SERIAL PRIMARY KEY,
            student_id INTEGER REFERENCES users(id),
            class_id INTEGER REFERENCES classes(id),
            enrolled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(student_id, class_id)
        )
    """)
    
    # OTP Codes table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS otp_codes (
            id SERIAL PRIMARY KEY,
            email VARCHAR(100) NOT NULL,
            phone VARCHAR(20),
            code VARCHAR(10) NOT NULL,
            purpose VARCHAR(50) NOT NULL,
            expires_at TIMESTAMP NOT NULL,
            is_used BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Notifications table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notifications (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id),
            title VARCHAR(200) NOT NULL,
            message TEXT NOT NULL,
            type VARCHAR(50) DEFAULT 'info',
            is_read BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Subject Teachers table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS subject_teachers (
            id SERIAL PRIMARY KEY,
            teacher_id INTEGER REFERENCES users(id),
            subject_id INTEGER REFERENCES subjects(id),
            status VARCHAR(20) DEFAULT 'pending',
            invited_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            accepted_at TIMESTAMP,
            UNIQUE(teacher_id, subject_id)
        )
    """)
    
    # Student Subjects table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS student_subjects (
            id SERIAL PRIMARY KEY,
            student_id INTEGER REFERENCES users(id),
            subject_id INTEGER REFERENCES subjects(id),
            status VARCHAR(20) DEFAULT 'pending',
            requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            approved_at TIMESTAMP,
            UNIQUE(student_id, subject_id)
        )
    """)
    
    # Weaknesses table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS weaknesses (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id),
            subject_id INTEGER REFERENCES subjects(id),
            weakness_type VARCHAR(100) NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create indexes
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)",
        "CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)",
        "CREATE INDEX IF NOT EXISTS idx_users_role ON users(role)",
        "CREATE INDEX IF NOT EXISTS idx_quizzes_subject ON quizzes(subject_id)",
        "CREATE INDEX IF NOT EXISTS idx_questions_quiz ON questions(quiz_id)",
        "CREATE INDEX IF NOT EXISTS idx_results_user ON results(user_id)",
        "CREATE INDEX IF NOT EXISTS idx_results_quiz ON results(quiz_id)",
        "CREATE INDEX IF NOT EXISTS idx_notifications_user ON notifications(user_id)",
        "CREATE INDEX IF NOT EXISTS idx_subject_teachers_teacher ON subject_teachers(teacher_id)",
        "CREATE INDEX IF NOT EXISTS idx_subject_teachers_subject ON subject_teachers(subject_id)",
        "CREATE INDEX IF NOT EXISTS idx_student_subjects_student ON student_subjects(student_id)",
        "CREATE INDEX IF NOT EXISTS idx_student_subjects_subject ON student_subjects(subject_id)",
        "CREATE INDEX IF NOT EXISTS idx_weaknesses_user ON weaknesses(user_id)",
        "CREATE INDEX IF NOT EXISTS idx_weaknesses_subject ON weaknesses(subject_id)"
    ]
    
    for index_sql in indexes:
        cursor.execute(index_sql)
    
    conn.commit()
    print("  ✅ PostgreSQL schema created successfully")

def migrate_data(sqlite_conn, postgres_conn):
    """Migrate data from SQLite to PostgreSQL"""
    sqlite_cursor = sqlite_conn.cursor()
    postgres_cursor = postgres_conn.cursor()
    
    print("📦 Migrating data...")
    
    # Migrate users
    print("  📝 Migrating users...")
    sqlite_cursor.execute("SELECT * FROM users")
    users = sqlite_cursor.fetchall()
    
    for user in users:
        postgres_cursor.execute("""
            INSERT INTO users (id, username, password, role, email, full_name, user_id, is_active, last_login, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING
        """, user)
    
    # Migrate subjects
    print("  📝 Migrating subjects...")
    sqlite_cursor.execute("SELECT * FROM subjects")
    subjects = sqlite_cursor.fetchall()
    
    for subject in subjects:
        postgres_cursor.execute("""
            INSERT INTO subjects (id, name, description, created_at, created_by)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING
        """, subject)
    
    # Migrate quizzes
    print("  📝 Migrating quizzes...")
    sqlite_cursor.execute("SELECT * FROM quizzes")
    quizzes = sqlite_cursor.fetchall()
    
    for quiz in quizzes:
        postgres_cursor.execute("""
            INSERT INTO quizzes (id, title, description, subject_id, created_by, created_at, is_active)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING
        """, quiz)
    
    # Migrate questions
    print("  📝 Migrating questions...")
    sqlite_cursor.execute("SELECT * FROM questions")
    questions = sqlite_cursor.fetchall()
    
    for question in questions:
        postgres_cursor.execute("""
            INSERT INTO questions (id, quiz_id, question_text, question_type, options, correct_answer, points, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING
        """, question)
    
    # Migrate results
    print("  📝 Migrating results...")
    sqlite_cursor.execute("SELECT * FROM results")
    results = sqlite_cursor.fetchall()
    
    for result in results:
        postgres_cursor.execute("""
            INSERT INTO results (id, user_id, quiz_id, score, total_questions, percentage, answers, completed_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING
        """, result)
    
    # Migrate classes
    print("  📝 Migrating classes...")
    sqlite_cursor.execute("SELECT * FROM classes")
    classes = sqlite_cursor.fetchall()
    
    for class_item in classes:
        postgres_cursor.execute("""
            INSERT INTO classes (id, name, description, subject_id, created_by, created_at)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING
        """, class_item)
    
    # Migrate teacher_classes
    print("  📝 Migrating teacher_classes...")
    sqlite_cursor.execute("SELECT * FROM teacher_classes")
    teacher_classes = sqlite_cursor.fetchall()
    
    for tc in teacher_classes:
        postgres_cursor.execute("""
            INSERT INTO teacher_classes (id, teacher_id, class_id, assigned_at)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING
        """, tc)
    
    # Migrate student_classes
    print("  📝 Migrating student_classes...")
    sqlite_cursor.execute("SELECT * FROM student_classes")
    student_classes = sqlite_cursor.fetchall()
    
    for sc in student_classes:
        postgres_cursor.execute("""
            INSERT INTO student_classes (id, student_id, class_id, enrolled_at)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING
        """, sc)
    
    # Migrate otp_codes
    print("  📝 Migrating otp_codes...")
    sqlite_cursor.execute("SELECT * FROM otp_codes")
    otp_codes = sqlite_cursor.fetchall()
    
    for otp in otp_codes:
        postgres_cursor.execute("""
            INSERT INTO otp_codes (id, email, phone, code, purpose, expires_at, is_used, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING
        """, otp)
    
    # Migrate notifications
    print("  📝 Migrating notifications...")
    sqlite_cursor.execute("SELECT * FROM notifications")
    notifications = sqlite_cursor.fetchall()
    
    for notification in notifications:
        postgres_cursor.execute("""
            INSERT INTO notifications (id, user_id, title, message, type, is_read, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING
        """, notification)
    
    # Migrate subject_teachers
    print("  📝 Migrating subject_teachers...")
    sqlite_cursor.execute("SELECT * FROM subject_teachers")
    subject_teachers = sqlite_cursor.fetchall()
    
    for st in subject_teachers:
        postgres_cursor.execute("""
            INSERT INTO subject_teachers (id, teacher_id, subject_id, status, invited_at, accepted_at)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING
        """, st)
    
    # Migrate student_subjects
    print("  📝 Migrating student_subjects...")
    sqlite_cursor.execute("SELECT * FROM student_subjects")
    student_subjects = sqlite_cursor.fetchall()
    
    for ss in student_subjects:
        postgres_cursor.execute("""
            INSERT INTO student_subjects (id, student_id, subject_id, status, requested_at, approved_at)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING
        """, ss)
    
    # Migrate weaknesses
    print("  📝 Migrating weaknesses...")
    sqlite_cursor.execute("SELECT * FROM weaknesses")
    weaknesses = sqlite_cursor.fetchall()
    
    for weakness in weaknesses:
        postgres_cursor.execute("""
            INSERT INTO weaknesses (id, user_id, subject_id, weakness_type, description, created_at)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING
        """, weakness)
    
    postgres_conn.commit()
    print("  ✅ Data migration completed successfully")

def verify_migration(postgres_conn):
    """Verify the migration was successful"""
    cursor = postgres_conn.cursor()
    
    print("🔍 Verifying migration...")
    
    # Check user counts
    cursor.execute("SELECT role, COUNT(*) FROM users GROUP BY role")
    role_counts = cursor.fetchall()
    print("  👥 Users by role:")
    for role, count in role_counts:
        print(f"    {role.capitalize()}: {count}")
    
    # Check other tables
    tables = ['subjects', 'quizzes', 'questions', 'results', 'notifications', 'subject_teachers', 'student_subjects', 'weaknesses']
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"  📊 {table}: {count} records")
    
    print("  ✅ Migration verification completed")

def main():
    """Main migration function"""
    print("🚀 Starting SQLite to PostgreSQL Migration...")
    print("=" * 60)
    
    try:
        # Check if psycopg2 is available
        try:
            import psycopg2
        except ImportError:
            print("❌ psycopg2 not found. Please install it:")
            print("pip install psycopg2-binary")
            sys.exit(1)
        
        # Get connections
        print("📡 Connecting to databases...")
        sqlite_conn = get_sqlite_connection()
        postgres_conn = get_postgres_connection()
        print("  ✅ Connected to SQLite and PostgreSQL")
        
        # Create schema
        create_postgres_schema(postgres_conn)
        
        # Migrate data
        migrate_data(sqlite_conn, postgres_conn)
        
        # Verify migration
        verify_migration(postgres_conn)
        
        # Close connections
        sqlite_conn.close()
        postgres_conn.close()
        
        print("\n🎉 Migration completed successfully!")
        print("\n📋 Next steps for Render.com deployment:")
        print("  1. Set DATABASE_URL environment variable in Render.com")
        print("  2. Deploy your application")
        print("  3. Your data will be available in PostgreSQL")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()