#!/usr/bin/env python3
"""
AgriQuest - SQLite to PostgreSQL Migration Script
This script migrates your SQLite database to PostgreSQL
"""

import os
import sqlite3
import psycopg2
from psycopg2.extras import DictCursor
from urllib.parse import urlparse
from werkzeug.security import generate_password_hash
import json
from datetime import datetime

def get_sqlite_connection():
    """Get SQLite connection"""
    return sqlite3.connect('agriquest.db')

def get_postgresql_connection():
    """Get PostgreSQL connection from DATABASE_URL"""
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        raise Exception("DATABASE_URL environment variable not set")
    
    url = urlparse(database_url)
    return psycopg2.connect(
        database=url.path[1:],
        user=url.username,
        password=url.password,
        host=url.hostname,
        port=url.port
    )

def migrate_users(sqlite_conn, pg_conn):
    """Migrate users table"""
    print("📝 Migrating users...")
    
    sqlite_cursor = sqlite_conn.cursor()
    pg_cursor = pg_conn.cursor()
    
    # Get all users from SQLite
    sqlite_cursor.execute("SELECT * FROM users")
    users = sqlite_cursor.fetchall()
    
    # Get column names
    columns = [description[0] for description in sqlite_cursor.description]
    
    for user in users:
        user_dict = dict(zip(columns, user))
        
        # Insert into PostgreSQL
        insert_sql = """
        INSERT INTO users (id, username, email, password_hash, full_name, role, user_id, is_active, last_login, created_at)
        VALUES (%(id)s, %(username)s, %(email)s, %(password_hash)s, %(full_name)s, %(role)s, %(user_id)s, %(is_active)s, %(last_login)s, %(created_at)s)
        ON CONFLICT (id) DO NOTHING
        """
        
        pg_cursor.execute(insert_sql, user_dict)
    
    print(f"   ✅ Migrated {len(users)} users")
    pg_conn.commit()

def migrate_subjects(sqlite_conn, pg_conn):
    """Migrate subjects table"""
    print("📝 Migrating subjects...")
    
    sqlite_cursor = sqlite_conn.cursor()
    pg_cursor = pg_conn.cursor()
    
    sqlite_cursor.execute("SELECT * FROM subjects")
    subjects = sqlite_cursor.fetchall()
    
    columns = [description[0] for description in sqlite_cursor.description]
    
    for subject in subjects:
        subject_dict = dict(zip(columns, subject))
        
        insert_sql = """
        INSERT INTO subjects (id, name, description, created_at)
        VALUES (%(id)s, %(name)s, %(description)s, %(created_at)s)
        ON CONFLICT (id) DO NOTHING
        """
        
        pg_cursor.execute(insert_sql, subject_dict)
    
    print(f"   ✅ Migrated {len(subjects)} subjects")
    pg_conn.commit()

def migrate_quizzes(sqlite_conn, pg_conn):
    """Migrate quizzes table"""
    print("📝 Migrating quizzes...")
    
    sqlite_cursor = sqlite_conn.cursor()
    pg_cursor = pg_conn.cursor()
    
    sqlite_cursor.execute("SELECT * FROM quizzes")
    quizzes = sqlite_cursor.fetchall()
    
    columns = [description[0] for description in sqlite_cursor.description]
    
    for quiz in quizzes:
        quiz_dict = dict(zip(columns, quiz))
        
        insert_sql = """
        INSERT INTO quizzes (id, subject_id, title, description, questions, created_at, updated_at)
        VALUES (%(id)s, %(subject_id)s, %(title)s, %(description)s, %(questions)s, %(created_at)s, %(updated_at)s)
        ON CONFLICT (id) DO NOTHING
        """
        
        pg_cursor.execute(insert_sql, quiz_dict)
    
    print(f"   ✅ Migrated {len(quizzes)} quizzes")
    pg_conn.commit()

def migrate_results(sqlite_conn, pg_conn):
    """Migrate results table"""
    print("📝 Migrating results...")
    
    sqlite_cursor = sqlite_conn.cursor()
    pg_cursor = pg_conn.cursor()
    
    sqlite_cursor.execute("SELECT * FROM results")
    results = sqlite_cursor.fetchall()
    
    columns = [description[0] for description in sqlite_cursor.description]
    
    for result in results:
        result_dict = dict(zip(columns, result))
        
        insert_sql = """
        INSERT INTO results (id, user_id, quiz_id, score, total_questions, answers, completed_at)
        VALUES (%(id)s, %(user_id)s, %(quiz_id)s, %(score)s, %(total_questions)s, %(answers)s, %(completed_at)s)
        ON CONFLICT (id) DO NOTHING
        """
        
        pg_cursor.execute(insert_sql, result_dict)
    
    print(f"   ✅ Migrated {len(results)} results")
    pg_conn.commit()

def migrate_new_tables(sqlite_conn, pg_conn):
    """Migrate new V2 tables"""
    print("📝 Migrating V2 tables...")
    
    # Migrate notifications
    try:
        sqlite_cursor = sqlite_conn.cursor()
        pg_cursor = pg_conn.cursor()
        
        sqlite_cursor.execute("SELECT * FROM notifications")
        notifications = sqlite_cursor.fetchall()
        
        if notifications:
            columns = [description[0] for description in sqlite_cursor.description]
            
            for notification in notifications:
                notification_dict = dict(zip(columns, notification))
                
                insert_sql = """
                INSERT INTO notifications (id, user_id, title, message, type, is_read, created_at)
                VALUES (%(id)s, %(user_id)s, %(title)s, %(message)s, %(type)s, %(is_read)s, %(created_at)s)
                ON CONFLICT (id) DO NOTHING
                """
                
                pg_cursor.execute(insert_sql, notification_dict)
            
            print(f"   ✅ Migrated {len(notifications)} notifications")
            pg_conn.commit()
    except Exception as e:
        print(f"   ⚠️  Notifications table not found or empty: {e}")
    
    # Migrate subject_teachers
    try:
        sqlite_cursor.execute("SELECT * FROM subject_teachers")
        subject_teachers = sqlite_cursor.fetchall()
        
        if subject_teachers:
            columns = [description[0] for description in sqlite_cursor.description]
            
            for st in subject_teachers:
                st_dict = dict(zip(columns, st))
                
                insert_sql = """
                INSERT INTO subject_teachers (id, teacher_id, subject_id, status, invited_at, accepted_at)
                VALUES (%(id)s, %(teacher_id)s, %(subject_id)s, %(status)s, %(invited_at)s, %(accepted_at)s)
                ON CONFLICT (id) DO NOTHING
                """
                
                pg_cursor.execute(insert_sql, st_dict)
            
            print(f"   ✅ Migrated {len(subject_teachers)} subject_teachers")
            pg_conn.commit()
    except Exception as e:
        print(f"   ⚠️  Subject_teachers table not found or empty: {e}")
    
    # Migrate student_subjects
    try:
        sqlite_cursor.execute("SELECT * FROM student_subjects")
        student_subjects = sqlite_cursor.fetchall()
        
        if student_subjects:
            columns = [description[0] for description in sqlite_cursor.description]
            
            for ss in student_subjects:
                ss_dict = dict(zip(columns, ss))
                
                insert_sql = """
                INSERT INTO student_subjects (id, student_id, subject_id, status, requested_at, approved_at)
                VALUES (%(id)s, %(student_id)s, %(subject_id)s, %(status)s, %(requested_at)s, %(approved_at)s)
                ON CONFLICT (id) DO NOTHING
                """
                
                pg_cursor.execute(insert_sql, ss_dict)
            
            print(f"   ✅ Migrated {len(student_subjects)} student_subjects")
            pg_conn.commit()
    except Exception as e:
        print(f"   ⚠️  Student_subjects table not found or empty: {e}")
    
    # Migrate weaknesses
    try:
        sqlite_cursor.execute("SELECT * FROM weaknesses")
        weaknesses = sqlite_cursor.fetchall()
        
        if weaknesses:
            columns = [description[0] for description in sqlite_cursor.description]
            
            for weakness in weaknesses:
                weakness_dict = dict(zip(columns, weakness))
                
                insert_sql = """
                INSERT INTO weaknesses (id, user_id, subject_id, weakness_type, description, created_at)
                VALUES (%(id)s, %(user_id)s, %(subject_id)s, %(weakness_type)s, %(description)s, %(created_at)s)
                ON CONFLICT (id) DO NOTHING
                """
                
                pg_cursor.execute(insert_sql, weakness_dict)
            
            print(f"   ✅ Migrated {len(weaknesses)} weaknesses")
            pg_conn.commit()
    except Exception as e:
        print(f"   ⚠️  Weaknesses table not found or empty: {e}")

def create_postgresql_schema(pg_conn):
    """Create PostgreSQL schema"""
    print("📝 Creating PostgreSQL schema...")
    
    cursor = pg_conn.cursor()
    
    # Create tables with PostgreSQL syntax
    schema_sql = """
    -- Users table
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        username VARCHAR(50) UNIQUE NOT NULL,
        email VARCHAR(100) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        full_name VARCHAR(100) NOT NULL,
        role VARCHAR(20) NOT NULL CHECK (role IN ('admin', 'teacher', 'student')),
        user_id VARCHAR(20) UNIQUE,
        is_active BOOLEAN DEFAULT TRUE,
        last_login TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    -- Subjects table
    CREATE TABLE IF NOT EXISTS subjects (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    -- Quizzes table
    CREATE TABLE IF NOT EXISTS quizzes (
        id SERIAL PRIMARY KEY,
        subject_id INTEGER REFERENCES subjects(id) ON DELETE CASCADE,
        title VARCHAR(200) NOT NULL,
        description TEXT,
        questions JSONB NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    -- Results table
    CREATE TABLE IF NOT EXISTS results (
        id SERIAL PRIMARY KEY,
        user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
        quiz_id INTEGER REFERENCES quizzes(id) ON DELETE CASCADE,
        score INTEGER NOT NULL,
        total_questions INTEGER NOT NULL,
        answers JSONB NOT NULL,
        completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    -- Notifications table
    CREATE TABLE IF NOT EXISTS notifications (
        id SERIAL PRIMARY KEY,
        user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
        title VARCHAR(200) NOT NULL,
        message TEXT NOT NULL,
        type VARCHAR(50) DEFAULT 'info',
        is_read BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    -- Subject Teachers table
    CREATE TABLE IF NOT EXISTS subject_teachers (
        id SERIAL PRIMARY KEY,
        teacher_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
        subject_id INTEGER REFERENCES subjects(id) ON DELETE CASCADE,
        status VARCHAR(20) DEFAULT 'pending',
        invited_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        accepted_at TIMESTAMP,
        UNIQUE(teacher_id, subject_id)
    );
    
    -- Student Subjects table
    CREATE TABLE IF NOT EXISTS student_subjects (
        id SERIAL PRIMARY KEY,
        student_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
        subject_id INTEGER REFERENCES subjects(id) ON DELETE CASCADE,
        status VARCHAR(20) DEFAULT 'pending',
        requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        approved_at TIMESTAMP,
        UNIQUE(student_id, subject_id)
    );
    
    -- Weaknesses table
    CREATE TABLE IF NOT EXISTS weaknesses (
        id SERIAL PRIMARY KEY,
        user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
        subject_id INTEGER REFERENCES subjects(id) ON DELETE CASCADE,
        weakness_type VARCHAR(100) NOT NULL,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    -- Create indexes
    CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
    CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
    CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
    CREATE INDEX IF NOT EXISTS idx_quizzes_subject_id ON quizzes(subject_id);
    CREATE INDEX IF NOT EXISTS idx_results_user_id ON results(user_id);
    CREATE INDEX IF NOT EXISTS idx_results_quiz_id ON results(quiz_id);
    CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON notifications(user_id);
    CREATE INDEX IF NOT EXISTS idx_subject_teachers_teacher_id ON subject_teachers(teacher_id);
    CREATE INDEX IF NOT EXISTS idx_student_subjects_student_id ON student_subjects(student_id);
    CREATE INDEX IF NOT EXISTS idx_weaknesses_user_id ON weaknesses(user_id);
    """
    
    cursor.execute(schema_sql)
    pg_conn.commit()
    print("   ✅ PostgreSQL schema created")

def main():
    """Main migration function"""
    print("🚀 AgriQuest SQLite to PostgreSQL Migration")
    print("=" * 60)
    
    # Check if DATABASE_URL is set
    if not os.getenv('DATABASE_URL'):
        print("❌ DATABASE_URL environment variable not set!")
        print("\n💡 To set up PostgreSQL:")
        print("1. Get a free database from Railway, Supabase, or Neon")
        print("2. Set DATABASE_URL environment variable:")
        print("   export DATABASE_URL='postgres://username:password@host:port/database'")
        print("3. Run this script again")
        return
    
    try:
        # Connect to databases
        print("🔌 Connecting to databases...")
        sqlite_conn = get_sqlite_connection()
        pg_conn = get_postgresql_connection()
        print("   ✅ Connected to SQLite and PostgreSQL")
        
        # Create PostgreSQL schema
        create_postgresql_schema(pg_conn)
        
        # Migrate data
        print("\n📦 Migrating data...")
        migrate_users(sqlite_conn, pg_conn)
        migrate_subjects(sqlite_conn, pg_conn)
        migrate_quizzes(sqlite_conn, pg_conn)
        migrate_results(sqlite_conn, pg_conn)
        migrate_new_tables(sqlite_conn, pg_conn)
        
        # Close connections
        sqlite_conn.close()
        pg_conn.close()
        
        print("\n🎉 Migration completed successfully!")
        print("✅ Your data has been migrated to PostgreSQL")
        print("✅ You can now use PostgreSQL by setting DATABASE_URL")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        print("💡 Make sure your PostgreSQL database is accessible and DATABASE_URL is correct")

if __name__ == "__main__":
    main()
