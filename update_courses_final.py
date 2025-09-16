#!/usr/bin/env python3
"""
AgriQuest - Final Course Update
Updates subjects with new BS Agriculture courses, adding required columns first
"""

import os
import sys
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

def update_database_schema(conn):
    """Update database schema to include year and code fields"""
    print("🔧 Updating database schema...")
    
    cursor = conn.cursor()
    
    try:
        # Add year column if it doesn't exist
        cursor.execute("""
            ALTER TABLE subjects 
            ADD COLUMN IF NOT EXISTS year INTEGER
        """)
        print("   ✅ Added year column to subjects table")
        
        # Add code column if it doesn't exist
        cursor.execute("""
            ALTER TABLE subjects 
            ADD COLUMN IF NOT EXISTS code VARCHAR(20)
        """)
        print("   ✅ Added code column to subjects table")
        
        conn.commit()
        print("   📊 Database schema updated successfully")
        
    except Exception as e:
        print(f"   ❌ Error updating schema: {e}")
        conn.rollback()
        raise

def clear_existing_subjects(conn):
    """Remove all existing subjects"""
    print("🗑️  Clearing existing subjects...")
    
    cursor = conn.cursor()
    
    try:
        # Delete existing subjects
        cursor.execute("DELETE FROM subjects")
        print("   ✅ Cleared subjects table")
        
        conn.commit()
        print("   📊 All existing subjects removed")
        
    except Exception as e:
        print(f"   ❌ Error clearing subjects: {e}")
        conn.rollback()
        raise

def create_new_subjects(conn):
    """Create new BS Agriculture subjects"""
    print("\n📚 Creating new BS Agriculture subjects...")
    
    cursor = conn.cursor()
    
    # Define the new subjects
    subjects = [
        # Year 1 - Introductory Agriculture Courses
        {
            'name': 'Introduction to Agriculture',
            'description': 'Overview of agriculture, its importance, and basic concepts in agricultural science.',
            'year': 1,
            'code': 'AGRI-101'
        },
        {
            'name': 'Fundamentals of Crop Science I',
            'description': 'Basic principles of crop production, plant growth, and development.',
            'year': 1,
            'code': 'AGRI-102'
        },
        {
            'name': 'Fundamentals of Soil Science I',
            'description': 'Introduction to soil properties, composition, and basic soil management.',
            'year': 1,
            'code': 'AGRI-103'
        },
        {
            'name': 'Introduction to Animal Science',
            'description': 'Basic concepts of animal production, nutrition, and husbandry.',
            'year': 1,
            'code': 'AGRI-104'
        },
        
        # Year 2 - Core Agriculture Courses
        {
            'name': 'Fundamentals of Crop Science II',
            'description': 'Advanced crop production techniques, breeding, and biotechnology.',
            'year': 2,
            'code': 'AGRI-201'
        },
        {
            'name': 'Soil Science II',
            'description': 'Advanced soil chemistry, fertility, and sustainable soil management.',
            'year': 2,
            'code': 'AGRI-202'
        },
        {
            'name': 'Animal Science II',
            'description': 'Advanced animal nutrition, breeding, and production systems.',
            'year': 2,
            'code': 'AGRI-203'
        },
        {
            'name': 'General Entomology',
            'description': 'Study of insects, their role in agriculture, and pest management.',
            'year': 2,
            'code': 'AGRI-204'
        },
        {
            'name': 'Plant Pathology (Intro)',
            'description': 'Introduction to plant diseases, their causes, and management strategies.',
            'year': 2,
            'code': 'AGRI-205'
        },
        {
            'name': 'Agricultural Extension & Communication (Intro)',
            'description': 'Principles of agricultural extension, communication, and rural development.',
            'year': 2,
            'code': 'AGRI-206'
        }
    ]
    
    # Insert subjects
    for subject in subjects:
        cursor.execute("""
            INSERT INTO subjects (name, description, year, code, created_at)
            VALUES (%(name)s, %(description)s, %(year)s, %(code)s, CURRENT_TIMESTAMP)
        """, subject)
        print(f"   ✅ Created: {subject['name']} (Year {subject['year']})")
    
    conn.commit()
    print(f"   📊 Created {len(subjects)} new agriculture subjects")

def main():
    """Main function to update agriculture courses"""
    print("🌱 AgriQuest - Final Course Update")
    print("=" * 50)
    print("This will update your subjects with proper BS Agriculture courses.")
    print()
    
    # Confirm with user
    response = input("Are you sure you want to proceed? This will remove all existing subjects. (yes/no): ").strip().lower()
    if response not in ['yes', 'y']:
        print("❌ Update cancelled.")
        return
    
    try:
        # Connect to database
        print("🔌 Connecting to database...")
        conn = get_database_connection()
        if not conn:
            print("❌ Failed to connect to database")
            return
        print("   ✅ Connected to database")
        
        # Update database schema
        update_database_schema(conn)
        
        # Clear existing subjects
        clear_existing_subjects(conn)
        
        # Create new subjects
        create_new_subjects(conn)
        
        conn.close()
        
        print("\n🎉 Agriculture courses update completed successfully!")
        print("✅ Database schema updated")
        print("✅ All existing subjects removed")
        print("✅ 10 new BS Agriculture subjects created")
        print("✅ Subjects organized by year (1st and 2nd year)")
        
        print("\n📚 New Subjects:")
        print("Year 1:")
        print("  1. Introduction to Agriculture")
        print("  2. Fundamentals of Crop Science I")
        print("  3. Fundamentals of Soil Science I")
        print("  4. Introduction to Animal Science")
        print("Year 2:")
        print("  5. Fundamentals of Crop Science II")
        print("  6. Soil Science II")
        print("  7. Animal Science II")
        print("  8. General Entomology")
        print("  9. Plant Pathology (Intro)")
        print("  10. Agricultural Extension & Communication (Intro)")
        
    except Exception as e:
        print(f"\n❌ Update failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
