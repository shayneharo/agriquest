#!/usr/bin/env python3
"""
AgriQuest - Update Agriculture Courses
Updates the system to use proper BS Agriculture 1st and 2nd year courses
"""

import os
import sys
import psycopg2
from urllib.parse import urlparse
from werkzeug.security import generate_password_hash

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

def clear_existing_subjects(conn):
    """Remove all existing subjects and related data"""
    print("🗑️  Clearing existing subjects and related data...")
    
    cursor = conn.cursor()
    
    try:
        # Delete in order to respect foreign key constraints
        tables_to_clear = [
            'weaknesses',
            'results', 
            'quizzes',
            'student_subjects',
            'subject_teachers',
            'subjects'
        ]
        
        for table in tables_to_clear:
            cursor.execute(f"DELETE FROM {table}")
            print(f"   ✅ Cleared {table}")
        
        conn.commit()
        print("   📊 All existing subjects and related data removed")
        
    except Exception as e:
        print(f"   ❌ Error clearing data: {e}")
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
            'id': 1,
            'name': 'Introduction to Agriculture',
            'description': 'Overview of agriculture, its importance, and basic concepts in agricultural science.',
            'year': 1,
            'code': 'AGRI-101'
        },
        {
            'id': 2,
            'name': 'Fundamentals of Crop Science I',
            'description': 'Basic principles of crop production, plant growth, and development.',
            'year': 1,
            'code': 'AGRI-102'
        },
        {
            'id': 3,
            'name': 'Fundamentals of Soil Science I',
            'description': 'Introduction to soil properties, composition, and basic soil management.',
            'year': 1,
            'code': 'AGRI-103'
        },
        {
            'id': 4,
            'name': 'Introduction to Animal Science',
            'description': 'Basic concepts of animal production, nutrition, and husbandry.',
            'year': 1,
            'code': 'AGRI-104'
        },
        
        # Year 2 - Core Agriculture Courses
        {
            'id': 5,
            'name': 'Fundamentals of Crop Science II',
            'description': 'Advanced crop production techniques, breeding, and biotechnology.',
            'year': 2,
            'code': 'AGRI-201'
        },
        {
            'id': 6,
            'name': 'Soil Science II',
            'description': 'Advanced soil chemistry, fertility, and sustainable soil management.',
            'year': 2,
            'code': 'AGRI-202'
        },
        {
            'id': 7,
            'name': 'Animal Science II',
            'description': 'Advanced animal nutrition, breeding, and production systems.',
            'year': 2,
            'code': 'AGRI-203'
        },
        {
            'id': 8,
            'name': 'General Entomology',
            'description': 'Study of insects, their role in agriculture, and pest management.',
            'year': 2,
            'code': 'AGRI-204'
        },
        {
            'id': 9,
            'name': 'Plant Pathology (Intro)',
            'description': 'Introduction to plant diseases, their causes, and management strategies.',
            'year': 2,
            'code': 'AGRI-205'
        },
        {
            'id': 10,
            'name': 'Agricultural Extension & Communication (Intro)',
            'description': 'Principles of agricultural extension, communication, and rural development.',
            'year': 2,
            'code': 'AGRI-206'
        }
    ]
    
    # Insert subjects
    for subject in subjects:
        cursor.execute("""
            INSERT INTO subjects (id, name, description, year, code, created_at)
            VALUES (%(id)s, %(name)s, %(description)s, %(year)s, %(code)s, CURRENT_TIMESTAMP)
        """, subject)
        print(f"   ✅ Created: {subject['name']} (Year {subject['year']})")
    
    conn.commit()
    print(f"   📊 Created {len(subjects)} new agriculture subjects")

def update_database_schema(conn):
    """Update database schema to include year and code fields"""
    print("\n🔧 Updating database schema...")
    
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

def create_sample_quizzes(conn):
    """Create sample quizzes for each subject"""
    print("\n📝 Creating sample quizzes for each subject...")
    
    cursor = conn.cursor()
    
    # Sample quiz questions for each subject
    quiz_templates = {
        1: {  # Introduction to Agriculture
            'title': 'Introduction to Agriculture - Quiz 1',
            'description': 'Basic concepts and principles of agriculture',
            'questions': [
                {
                    'question': 'What is the primary purpose of agriculture?',
                    'options': ['Food production', 'Entertainment', 'Transportation', 'Communication'],
                    'correct': 0
                },
                {
                    'question': 'Which of the following is NOT a branch of agriculture?',
                    'options': ['Crop Science', 'Animal Science', 'Soil Science', 'Computer Science'],
                    'correct': 3
                }
            ]
        },
        2: {  # Fundamentals of Crop Science I
            'title': 'Crop Science I - Plant Growth Quiz',
            'description': 'Basic principles of plant growth and development',
            'questions': [
                {
                    'question': 'What are the three main macronutrients for plants?',
                    'options': ['N, P, K', 'C, H, O', 'Fe, Zn, Mn', 'Ca, Mg, S'],
                    'correct': 0
                },
                {
                    'question': 'Which part of the plant is responsible for photosynthesis?',
                    'options': ['Roots', 'Stems', 'Leaves', 'Flowers'],
                    'correct': 2
                }
            ]
        },
        3: {  # Fundamentals of Soil Science I
            'title': 'Soil Science I - Soil Properties Quiz',
            'description': 'Basic soil properties and composition',
            'questions': [
                {
                    'question': 'What are the three main components of soil?',
                    'options': ['Sand, silt, clay', 'Water, air, minerals', 'Organic matter, minerals, water', 'All of the above'],
                    'correct': 3
                }
            ]
        },
        4: {  # Introduction to Animal Science
            'title': 'Animal Science I - Basic Concepts Quiz',
            'description': 'Introduction to animal production and nutrition',
            'questions': [
                {
                    'question': 'What is the primary purpose of animal science?',
                    'options': ['Pet care', 'Food production', 'Entertainment', 'Transportation'],
                    'correct': 1
                }
            ]
        },
        5: {  # Fundamentals of Crop Science II
            'title': 'Crop Science II - Advanced Techniques Quiz',
            'description': 'Advanced crop production and biotechnology',
            'questions': [
                {
                    'question': 'What is plant breeding?',
                    'options': ['Growing plants', 'Selecting and crossing plants', 'Harvesting crops', 'Selling plants'],
                    'correct': 1
                }
            ]
        },
        6: {  # Soil Science II
            'title': 'Soil Science II - Soil Fertility Quiz',
            'description': 'Advanced soil chemistry and fertility management',
            'questions': [
                {
                    'question': 'What is soil pH?',
                    'options': ['Soil color', 'Soil acidity/alkalinity', 'Soil texture', 'Soil temperature'],
                    'correct': 1
                }
            ]
        },
        7: {  # Animal Science II
            'title': 'Animal Science II - Nutrition Quiz',
            'description': 'Advanced animal nutrition and breeding',
            'questions': [
                {
                    'question': 'What are the main components of animal feed?',
                    'options': ['Protein, carbohydrates, fats', 'Vitamins, minerals, water', 'Both A and B', 'None of the above'],
                    'correct': 2
                }
            ]
        },
        8: {  # General Entomology
            'title': 'Entomology - Insect Biology Quiz',
            'description': 'Basic insect biology and classification',
            'questions': [
                {
                    'question': 'How many legs do insects have?',
                    'options': ['4', '6', '8', '10'],
                    'correct': 1
                }
            ]
        },
        9: {  # Plant Pathology
            'title': 'Plant Pathology - Disease Identification Quiz',
            'description': 'Introduction to plant diseases and their causes',
            'questions': [
                {
                    'question': 'What causes plant diseases?',
                    'options': ['Only bacteria', 'Only fungi', 'Bacteria, fungi, viruses', 'Only viruses'],
                    'correct': 2
                }
            ]
        },
        10: {  # Agricultural Extension
            'title': 'Agricultural Extension - Communication Quiz',
            'description': 'Principles of agricultural extension and communication',
            'questions': [
                {
                    'question': 'What is agricultural extension?',
                    'options': ['Growing crops', 'Teaching farmers', 'Selling products', 'Research only'],
                    'correct': 1
                }
            ]
        }
    }
    
    # Create quizzes for each subject
    for subject_id, quiz_data in quiz_templates.items():
        cursor.execute("""
            INSERT INTO quizzes (subject_id, title, description, questions, created_at, updated_at)
            VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """, (
            subject_id,
            quiz_data['title'],
            quiz_data['description'],
            str(quiz_data['questions']).replace("'", '"')  # Convert to JSON string
        ))
        print(f"   ✅ Created quiz for subject {subject_id}: {quiz_data['title']}")
    
    conn.commit()
    print(f"   📊 Created {len(quiz_templates)} sample quizzes")

def assign_teachers_to_subjects(conn):
    """Assign existing teachers to new subjects"""
    print("\n👨‍🏫 Assigning teachers to new subjects...")
    
    cursor = conn.cursor()
    
    # Get all teachers
    cursor.execute("SELECT id, username FROM users WHERE role = 'teacher'")
    teachers = cursor.fetchall()
    
    if not teachers:
        print("   ⚠️  No teachers found in the system")
        return
    
    # Get all subjects
    cursor.execute("SELECT id, name FROM subjects ORDER BY year, id")
    subjects = cursor.fetchall()
    
    # Assign teachers to subjects (distribute evenly)
    for i, subject in enumerate(subjects):
        teacher = teachers[i % len(teachers)]  # Distribute subjects among teachers
        cursor.execute("""
            INSERT INTO subject_teachers (teacher_id, subject_id, status, invited_at, accepted_at)
            VALUES (%s, %s, 'accepted', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """, (teacher[0], subject[0]))
        print(f"   ✅ Assigned {teacher[1]} to {subject[1]}")
    
    conn.commit()
    print(f"   📊 Assigned teachers to {len(subjects)} subjects")

def main():
    """Main function to update agriculture courses"""
    print("🌱 AgriQuest - Update Agriculture Courses")
    print("=" * 60)
    print("This will replace all existing subjects with proper BS Agriculture courses")
    print("for 1st and 2nd year students.")
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
        print("   ✅ Connected to database")
        
        # Update database schema
        update_database_schema(conn)
        
        # Clear existing subjects
        clear_existing_subjects(conn)
        
        # Create new subjects
        create_new_subjects(conn)
        
        # Create sample quizzes
        create_sample_quizzes(conn)
        
        # Assign teachers to subjects
        assign_teachers_to_subjects(conn)
        
        conn.close()
        
        print("\n🎉 Agriculture courses update completed successfully!")
        print("✅ All existing subjects removed")
        print("✅ 10 new BS Agriculture subjects created")
        print("✅ Subjects organized by year (1st and 2nd year)")
        print("✅ Sample quizzes created for each subject")
        print("✅ Teachers assigned to subjects")
        print("✅ Database schema updated")
        
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
