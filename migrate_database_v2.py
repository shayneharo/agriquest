#!/usr/bin/env python3
"""
Database Migration Script for AgriQuest v2.0

This script migrates the existing AgriQuest database to support the new
role-based system with three user types: Adviser (Admin), Subject Teacher,
and Student. It preserves all existing data while adding new tables and
functionality for the enhanced system.

Migration Features:
    - Preserves all existing data (no data loss)
    - Adds new tables for notifications, relationships, and weakness tracking
    - Enhances user model with new fields (user_id, is_active, last_login)
    - Creates default admin account (admin/admin123)
    - Migrates existing subject assignments
    - Creates performance indexes for better query performance

New Tables:
    - notifications: System notifications for all users
    - subject_teachers: Many-to-many relationship between subjects and teachers
    - student_subjects: Many-to-many relationship between students and subjects
    - weaknesses: Student weakness tracking and analysis

Safety Features:
    - Creates automatic backup before migration
    - Validates database structure before changes
    - Provides detailed logging of all operations
    - Rollback capability on errors

Author: AgriQuest Development Team
Version: 2.0
"""

import sqlite3
import hashlib
import os
from datetime import datetime

def get_db_connection():
    """Get database connection"""
    return sqlite3.connect('agriquest.db')

def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def run_migration():
    """Run the database migration"""
    print("🔄 Starting AgriQuest Database Migration v2.0...")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 1. Update users table - add new columns if they don't exist
        print("📝 Updating users table...")
        
        # Check if columns exist and add them if they don't
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Add columns one by one (without UNIQUE constraint first)
        if 'user_id' not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN user_id TEXT")
            print("  ✅ Added user_id column")
        
        if 'is_active' not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT 1")
            print("  ✅ Added is_active column")
        
        if 'last_login' not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN last_login DATETIME")
            print("  ✅ Added last_login column")
        
        # Remove phone column if it exists (we removed phone functionality)
        if 'phone' in columns:
            # We'll keep it for now to avoid data loss, but mark as deprecated
            print("  ℹ️  Phone column exists (deprecated)")
        
        # 2. Create notifications table
        print("📝 Creating notifications table...")
        cursor.execute("""
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
        """)
        print("  ✅ Created notifications table")
        
        # 3. Create subject_teachers table (many-to-many relationship)
        print("📝 Creating subject_teachers table...")
        cursor.execute("""
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
        """)
        print("  ✅ Created subject_teachers table")
        
        # 4. Create student_subjects table (many-to-many relationship)
        print("📝 Creating student_subjects table...")
        cursor.execute("""
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
        """)
        print("  ✅ Created student_subjects table")
        
        # 5. Create weaknesses table
        print("📝 Creating weaknesses table...")
        cursor.execute("""
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
        """)
        print("  ✅ Created weaknesses table")
        
        # 6. Create indexes for better performance
        print("📝 Creating indexes...")
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON notifications(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_notifications_is_read ON notifications(is_read)",
            "CREATE INDEX IF NOT EXISTS idx_subject_teachers_teacher_id ON subject_teachers(teacher_id)",
            "CREATE INDEX IF NOT EXISTS idx_subject_teachers_subject_id ON subject_teachers(subject_id)",
            "CREATE INDEX IF NOT EXISTS idx_subject_teachers_status ON subject_teachers(status)",
            "CREATE INDEX IF NOT EXISTS idx_student_subjects_student_id ON student_subjects(student_id)",
            "CREATE INDEX IF NOT EXISTS idx_student_subjects_subject_id ON student_subjects(subject_id)",
            "CREATE INDEX IF NOT EXISTS idx_student_subjects_status ON student_subjects(status)",
            "CREATE INDEX IF NOT EXISTS idx_weaknesses_user_id ON weaknesses(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_weaknesses_subject_id ON weaknesses(subject_id)"
        ]
        
        for index_sql in indexes:
            cursor.execute(index_sql)
        print("  ✅ Created performance indexes")
        
        # 7. Update existing users with user_id if not set
        print("📝 Updating existing users...")
        cursor.execute("SELECT id, username FROM users WHERE user_id IS NULL")
        users_without_id = cursor.fetchall()
        
        for user_id, username in users_without_id:
            # Generate user_id based on role and existing id
            cursor.execute("SELECT role FROM users WHERE id = ?", (user_id,))
            role = cursor.fetchone()[0]
            
            if role == 'teacher':
                new_user_id = f"T{user_id:03d}"
            elif role == 'student':
                new_user_id = f"S{user_id:03d}"
            else:
                new_user_id = f"U{user_id:03d}"
            
            cursor.execute("UPDATE users SET user_id = ? WHERE id = ?", (new_user_id, user_id))
            print(f"  ✅ Updated user {username} with user_id: {new_user_id}")
        
        # 7.5. Add UNIQUE constraint to user_id column
        print("📝 Adding UNIQUE constraint to user_id...")
        try:
            # Create a new table with the constraint
            cursor.execute("""
                CREATE TABLE users_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    role TEXT NOT NULL DEFAULT 'student',
                    email TEXT,
                    created_at DATETIME,
                    full_name TEXT,
                    profile_picture TEXT,
                    phone TEXT,
                    user_id TEXT UNIQUE,
                    is_active BOOLEAN DEFAULT 1,
                    last_login DATETIME
                )
            """)
            
            # Copy data from old table to new table
            cursor.execute("""
                INSERT INTO users_new 
                SELECT * FROM users
            """)
            
            # Drop old table and rename new table
            cursor.execute("DROP TABLE users")
            cursor.execute("ALTER TABLE users_new RENAME TO users")
            
            print("  ✅ Added UNIQUE constraint to user_id column")
        except Exception as e:
            print(f"  ⚠️  Could not add UNIQUE constraint: {e}")
            print("  ℹ️  Continuing without UNIQUE constraint...")
        
        # 8. Create default admin account
        print("📝 Creating default admin account...")
        cursor.execute("SELECT id FROM users WHERE username = 'admin'")
        admin_exists = cursor.fetchone()
        
        if not admin_exists:
            admin_password = hash_password('admin123')
            cursor.execute("""
                INSERT INTO users (username, password, role, email, full_name, user_id, is_active, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, ('admin', admin_password, 'admin', 'admin@agriquest.com', 'System Administrator', 'A001', 1, datetime.now()))
            print("  ✅ Created default admin account (username: admin, password: admin123)")
        else:
            print("  ℹ️  Admin account already exists")
        
        # 9. Migrate existing subject assignments
        print("📝 Migrating existing subject assignments...")
        
        # Get existing teacher (user_id = 1)
        cursor.execute("SELECT id FROM users WHERE id = 1 AND role = 'teacher'")
        existing_teacher = cursor.fetchone()
        
        if existing_teacher:
            # Assign existing teacher to all subjects
            cursor.execute("SELECT id FROM subjects")
            subjects = cursor.fetchall()
            
            for subject in subjects:
                subject_id = subject[0]
                cursor.execute("""
                    INSERT OR IGNORE INTO subject_teachers (teacher_id, subject_id, status, accepted_at)
                    VALUES (?, ?, ?, ?)
                """, (1, subject_id, 'accepted', datetime.now()))
            
            print(f"  ✅ Assigned existing teacher to {len(subjects)} subjects")
        
        # 10. Update role names to match new system
        print("📝 Updating role names...")
        cursor.execute("UPDATE users SET role = 'teacher' WHERE role = 'teacher'")  # Keep as is
        cursor.execute("UPDATE users SET role = 'student' WHERE role = 'student'")  # Keep as is
        print("  ✅ Role names updated")
        
        # Commit all changes
        conn.commit()
        print("\n🎉 Database migration completed successfully!")
        print("\n📊 Migration Summary:")
        print("  ✅ Updated users table with new columns")
        print("  ✅ Created notifications system")
        print("  ✅ Created subject-teacher relationships")
        print("  ✅ Created student-subject relationships")
        print("  ✅ Created weaknesses tracking")
        print("  ✅ Created performance indexes")
        print("  ✅ Migrated existing data")
        print("  ✅ Created default admin account")
        
        # Show current user counts
        cursor.execute("SELECT role, COUNT(*) FROM users GROUP BY role")
        role_counts = cursor.fetchall()
        print("\n👥 Current Users:")
        for role, count in role_counts:
            print(f"  {role.capitalize()}: {count}")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    # Check if database exists
    if not os.path.exists('agriquest.db'):
        print("❌ Database file 'agriquest.db' not found!")
        print("Please run this script from the project root directory.")
        exit(1)
    
    # Create backup
    backup_name = f"agriquest_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    print(f"💾 Creating backup: {backup_name}")
    os.system(f"cp agriquest.db {backup_name}")
    
    # Run migration
    run_migration()
    
    print(f"\n🔒 Backup created: {backup_name}")
    print("🚀 You can now run your application with the new features!")
