"""
Subject Model
Handles subject-related database operations
"""

from ..config.database import get_db_connection
import sqlite3

class Subject:
    @staticmethod
    def create_subject(name, description, created_by, year=None, code=None):
        conn = get_db_connection()
        try:
            conn.execute("INSERT INTO subjects (name, description, created_by, year, code) VALUES (?, ?, ?, ?, ?)",
                        (name, description, created_by, year, code))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
    
    @staticmethod
    def get_all_subjects():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''SELECT subjects.id, subjects.name, subjects.description, subjects.created_by, subjects.created_at, subjects.year, subjects.code, COALESCE(users.username, 'System') as creator_name 
                          FROM subjects LEFT JOIN users ON subjects.created_by = users.id
                          ORDER BY subjects.year, subjects.name''')
        subjects = cursor.fetchall()
        conn.close()
        
        # Convert tuples to dictionaries
        subject_dicts = []
        for subject in subjects:
            subject_dict = {
                'id': subject[0],
                'name': subject[1],
                'description': subject[2],
                'created_by': subject[3],
                'created_at': subject[4],
                'year': subject[5],
                'code': subject[6],
                'creator_name': subject[7]
            }
            subject_dicts.append(subject_dict)
        
        return subject_dicts
    
    @staticmethod
    def get_subject_by_id(subject_id):
        conn = get_db_connection()
        subject = conn.execute("SELECT * FROM subjects WHERE id = ?", (subject_id,)).fetchone()
        conn.close()
        return dict(subject) if subject else None
    
    @staticmethod
    def update_subject(subject_id, name, description):
        conn = get_db_connection()
        conn.execute("UPDATE subjects SET name = ?, description = ? WHERE id = ?", 
                    (name, description, subject_id))
        conn.commit()
        conn.close()
    
    @staticmethod
    def delete_subject(subject_id):
        conn = get_db_connection()
        conn.execute("DELETE FROM subjects WHERE id = ?", (subject_id,))
        conn.commit()
        conn.close()
