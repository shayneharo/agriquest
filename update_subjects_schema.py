#!/usr/bin/env python3
"""
AgriQuest - Update Subjects Schema
Adds year and code fields to subjects table for BS Agriculture courses
"""

import os
import sys
import psycopg2
from urllib.parse import urlparse

def get_database_connection():
    """Get database connection"""
    database_url = os.getenv('DATABASE_URL')
    
    if database_url and database_url.startswith('postgresql://'):
        url = urlparse(database_url)
        return psycopg2.connect(
            database=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
        )
    else:
        # Fallback to SQLite for local testing
        import sqlite3
        return sqlite3.connect('agriquest.db')

def update_subjects_schema(conn):
    """Update subjects table schema to include year and code fields"""
    print("🔧 Updating subjects table schema...")
    
    cursor = conn.cursor()
    
    try:
        # Check if we're using PostgreSQL or SQLite
        is_postgres = hasattr(conn, 'cursor_factory')
        
        if is_postgres:
            # PostgreSQL schema updates
            cursor.execute("""
                ALTER TABLE subjects 
                ADD COLUMN IF NOT EXISTS year INTEGER
            """)
            print("   ✅ Added year column to subjects table")
            
            cursor.execute("""
                ALTER TABLE subjects 
                ADD COLUMN IF NOT EXISTS code VARCHAR(20)
            """)
            print("   ✅ Added code column to subjects table")
            
        else:
            # SQLite schema updates
            try:
                cursor.execute("ALTER TABLE subjects ADD COLUMN year INTEGER")
                print("   ✅ Added year column to subjects table")
            except:
                print("   ⚠️  Year column already exists")
            
            try:
                cursor.execute("ALTER TABLE subjects ADD COLUMN code VARCHAR(20)")
                print("   ✅ Added code column to subjects table")
            except:
                print("   ⚠️  Code column already exists")
        
        conn.commit()
        print("   📊 Subjects table schema updated successfully")
        
    except Exception as e:
        print(f"   ❌ Error updating schema: {e}")
        conn.rollback()
        raise

def main():
    """Main function"""
    print("🔧 AgriQuest - Update Subjects Schema")
    print("=" * 50)
    
    try:
        # Connect to database
        print("🔌 Connecting to database...")
        conn = get_database_connection()
        print("   ✅ Connected to database")
        
        # Update schema
        update_subjects_schema(conn)
        
        conn.close()
        
        print("\n🎉 Schema update completed successfully!")
        print("✅ Subjects table now supports year and code fields")
        
    except Exception as e:
        print(f"\n❌ Schema update failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
