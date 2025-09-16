"""
Database Migration Script for API Tables - AgriQuest v2.0

This script ensures all required tables for the API functionality exist
in the database. It creates any missing tables and columns while preserving
existing data.

Tables Created/Updated:
    - notifications: User notifications
    - subject_teachers: Teacher-subject relationships
    - student_subjects: Student-subject relationships  
    - weaknesses: Student weakness tracking

Author: AgriQuest Development Team
Version: 2.0
"""

import sqlite3
import os
from datetime import datetime

def get_db_connection():
    """Get database connection"""
    return sqlite3.connect('agriquest.db')

def run_migration():
    """Run the migration"""
    print("🔄 Starting API tables migration...")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Create notifications table
        print("📧 Creating notifications table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                message TEXT NOT NULL,
                type TEXT NOT NULL DEFAULT 'info',
                is_read BOOLEAN DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        ''')
        
        # Create indexes for notifications
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_notifications_user_id 
            ON notifications(user_id)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_notifications_is_read 
            ON notifications(is_read)
        ''')
        
        # Create subject_teachers table
        print("👨‍🏫 Creating subject_teachers table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS subject_teachers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                teacher_id INTEGER NOT NULL,
                subject_id INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                invited_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                accepted_at DATETIME,
                FOREIGN KEY (teacher_id) REFERENCES users (id) ON DELETE CASCADE,
                FOREIGN KEY (subject_id) REFERENCES subjects (id) ON DELETE CASCADE,
                UNIQUE(teacher_id, subject_id)
            )
        ''')
        
        # Create indexes for subject_teachers
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_subject_teachers_teacher_id 
            ON subject_teachers(teacher_id)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_subject_teachers_subject_id 
            ON subject_teachers(subject_id)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_subject_teachers_status 
            ON subject_teachers(status)
        ''')
        
        # Create student_subjects table
        print("🎓 Creating student_subjects table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS student_subjects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                subject_id INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                requested_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                approved_at DATETIME,
                FOREIGN KEY (student_id) REFERENCES users (id) ON DELETE CASCADE,
                FOREIGN KEY (subject_id) REFERENCES subjects (id) ON DELETE CASCADE,
                UNIQUE(student_id, subject_id)
            )
        ''')
        
        # Create indexes for student_subjects
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_student_subjects_student_id 
            ON student_subjects(student_id)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_student_subjects_subject_id 
            ON student_subjects(subject_id)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_student_subjects_status 
            ON student_subjects(status)
        ''')
        
        # Create weaknesses table
        print("📊 Creating weaknesses table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS weaknesses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                subject_id INTEGER NOT NULL,
                weakness_type TEXT NOT NULL,
                description TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
                FOREIGN KEY (subject_id) REFERENCES subjects (id) ON DELETE CASCADE
            )
        ''')
        
        # Create indexes for weaknesses
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_weaknesses_user_id 
            ON weaknesses(user_id)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_weaknesses_subject_id 
            ON weaknesses(subject_id)
        ''')
        
        # Check if users table has required columns
        print("🔍 Checking users table structure...")
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Add missing columns if they don't exist
        if 'user_id' not in columns:
            print("➕ Adding user_id column to users table...")
            cursor.execute("ALTER TABLE users ADD COLUMN user_id TEXT UNIQUE")
        
        if 'is_active' not in columns:
            print("➕ Adding is_active column to users table...")
            cursor.execute("ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT 1")
        
        if 'last_login' not in columns:
            print("➕ Adding last_login column to users table...")
            cursor.execute("ALTER TABLE users ADD COLUMN last_login DATETIME")
        
        # Check if quizzes table has deadline column
        print("🔍 Checking quizzes table structure...")
        cursor.execute("PRAGMA table_info(quizzes)")
        quiz_columns = [column[1] for column in cursor.fetchall()]
        
        if 'deadline' not in quiz_columns:
            print("➕ Adding deadline column to quizzes table...")
            cursor.execute("ALTER TABLE quizzes ADD COLUMN deadline DATETIME")
        
        # Commit all changes
        conn.commit()
        print("✅ Migration completed successfully!")
        
        # Display table information
        print("\n📋 Database Tables:")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = cursor.fetchall()
        for table in tables:
            print(f"   - {table[0]}")
        
        print(f"\n🎉 API tables migration completed at {datetime.now()}")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    run_migration()

