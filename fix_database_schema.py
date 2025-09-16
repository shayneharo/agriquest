#!/usr/bin/env python3
"""
Fix database schema issues
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
        return None

def fix_database_schema():
    """Fix database schema issues"""
    print("🔧 Fixing database schema...")
    
    try:
        conn = get_database_connection()
        if not conn:
            print("❌ Failed to connect to database")
            return False
        
        cursor = conn.cursor()
        
        # Check if there are duplicate columns
        cursor.execute("""
            SELECT column_name, COUNT(*) 
            FROM information_schema.columns 
            WHERE table_name = 'subjects' 
            GROUP BY column_name 
            HAVING COUNT(*) > 1
        """)
        duplicates = cursor.fetchall()
        
        if duplicates:
            print(f"   ⚠️  Found duplicate columns: {duplicates}")
            # This shouldn't happen, but if it does, we need to handle it
        else:
            print("   ✅ No duplicate columns found")
        
        # Check current table structure
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'subjects' 
            ORDER BY ordinal_position
        """)
        columns = cursor.fetchall()
        
        print("   📊 Current subjects table structure:")
        for col in columns:
            print(f"      - {col[0]}: {col[1]}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

if __name__ == "__main__":
    fix_database_schema()
