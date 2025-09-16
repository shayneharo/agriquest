#!/usr/bin/env python3
"""
Check if quizzes exist in the system
"""

import psycopg2
from urllib.parse import urlparse

def get_database_connection():
    """Get database connection"""
    database_url = "postgresql://agriquest_user:45dtkZoHWC8uPDaj7nDPXG8qONxWxwIs@dpg-d34guuur433s73cjpo60-a.singapore-postgres.render.com/agriquest"
    
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
        print("❌ Invalid database URL format")
        return None

def check_quizzes():
    """Check if quizzes exist in the system"""
    print("🔍 Checking for quizzes in your system...")
    
    try:
        conn = get_database_connection()
        if not conn:
            print("❌ Failed to connect to database")
            return
        
        cursor = conn.cursor()
        
        # Check if quizzes table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'quizzes'
            );
        """)
        table_exists = cursor.fetchone()[0]
        
        if not table_exists:
            print("❌ Quizzes table does not exist")
            return
        
        # Count total quizzes
        cursor.execute("SELECT COUNT(*) FROM quizzes")
        quiz_count = cursor.fetchone()[0]
        
        print(f"📊 Total quizzes in system: {quiz_count}")
        
        if quiz_count > 0:
            # Get quiz details
            cursor.execute("""
                SELECT q.id, q.title, q.description, s.name as subject_name
                FROM quizzes q
                LEFT JOIN subjects s ON q.subject_id = s.id
                ORDER BY q.id
            """)
            quizzes = cursor.fetchall()
            
            print("\n📝 Existing Quizzes:")
            for quiz in quizzes:
                print(f"   {quiz[0]}. {quiz[1]}")
                print(f"      Subject: {quiz[3]}")
                print(f"      Description: {quiz[2]}")
                print()
        else:
            print("❌ No quizzes found in the system")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error checking quizzes: {e}")

if __name__ == "__main__":
    check_quizzes()
