"""
Weakness Model for AgriQuest v2.0

This module handles all weakness tracking database operations including
adding, retrieving, and analyzing student weaknesses across subjects.

Classes:
    Weakness: Main class for weakness operations

Methods:
    add_weakness: Add a weakness record for a student
    get_student_weaknesses: Get weaknesses for a specific student
    get_subject_weaknesses: Get weaknesses for a specific subject
    get_weakest_students: Get students with most weaknesses in a subject
    update_weakness: Update a weakness record
    delete_weakness: Delete a weakness record

Author: AgriQuest Development Team
Version: 2.0
"""

from ..config.database import get_db_connection
import sqlite3

class Weakness:
    @staticmethod
    def add_weakness(user_id, subject_id, weakness_type, description=None):
        """Add a weakness record for a student"""
        conn = get_db_connection()
        try:
            conn.execute("""
                INSERT INTO weaknesses (user_id, subject_id, weakness_type, description, created_at) 
                VALUES (?, ?, ?, ?, datetime('now'))
            """, (user_id, subject_id, weakness_type, description))
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error adding weakness: {e}")
            return False
        finally:
            conn.close()
    
    @staticmethod
    def get_student_weaknesses(user_id, subject_id=None):
        """Get weaknesses for a specific student"""
        conn = get_db_connection()
        try:
            if subject_id:
                weaknesses = conn.execute("""
                    SELECT w.*, s.name as subject_name
                    FROM weaknesses w
                    JOIN subjects s ON w.subject_id = s.id
                    WHERE w.user_id = ? AND w.subject_id = ?
                    ORDER BY w.created_at DESC
                """, (user_id, subject_id)).fetchall()
            else:
                weaknesses = conn.execute("""
                    SELECT w.*, s.name as subject_name
                    FROM weaknesses w
                    JOIN subjects s ON w.subject_id = s.id
                    WHERE w.user_id = ?
                    ORDER BY w.created_at DESC
                """, (user_id,)).fetchall()
            return [dict(weakness) for weakness in weaknesses]
        except sqlite3.Error as e:
            print(f"Error getting student weaknesses: {e}")
            return []
        finally:
            conn.close()
    
    @staticmethod
    def get_subject_weaknesses(subject_id):
        """Get weaknesses for a specific subject"""
        conn = get_db_connection()
        try:
            weaknesses = conn.execute("""
                SELECT w.*, u.username, u.full_name
                FROM weaknesses w
                JOIN users u ON w.user_id = u.id
                WHERE w.subject_id = ?
                ORDER BY w.created_at DESC
            """, (subject_id,)).fetchall()
            return [dict(weakness) for weakness in weaknesses]
        except sqlite3.Error as e:
            print(f"Error getting subject weaknesses: {e}")
            return []
        finally:
            conn.close()
    
    @staticmethod
    def get_weakest_students(subject_id, limit=10):
        """Get students with most weaknesses in a subject"""
        conn = get_db_connection()
        try:
            students = conn.execute("""
                SELECT u.*, COUNT(w.id) as weakness_count
                FROM users u
                JOIN weaknesses w ON u.id = w.user_id
                WHERE w.subject_id = ? AND u.role = 'student'
                GROUP BY u.id
                ORDER BY weakness_count DESC
                LIMIT ?
            """, (subject_id, limit)).fetchall()
            return [dict(student) for student in students]
        except sqlite3.Error as e:
            print(f"Error getting weakest students: {e}")
            return []
        finally:
            conn.close()
    
    @staticmethod
    def update_weakness(weakness_id, weakness_type=None, description=None):
        """Update a weakness record"""
        conn = get_db_connection()
        try:
            updates = []
            params = []
            
            if weakness_type is not None:
                updates.append("weakness_type = ?")
                params.append(weakness_type)
            
            if description is not None:
                updates.append("description = ?")
                params.append(description)
            
            if updates:
                params.append(weakness_id)
                query = f"UPDATE weaknesses SET {', '.join(updates)} WHERE id = ?"
                conn.execute(query, params)
                conn.commit()
                return True
            return False
        except sqlite3.Error as e:
            print(f"Error updating weakness: {e}")
            return False
        finally:
            conn.close()
    
    @staticmethod
    def delete_weakness(weakness_id):
        """Delete a weakness record"""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM weaknesses WHERE id = ?", (weakness_id,))
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Error deleting weakness: {e}")
            return False
        finally:
            conn.close()
    
    @staticmethod
    def get_weakness_statistics(user_id):
        """Get weakness statistics for a student"""
        conn = get_db_connection()
        try:
            # Get total weaknesses by subject
            stats = conn.execute("""
                SELECT s.name as subject_name, COUNT(w.id) as weakness_count
                FROM subjects s
                LEFT JOIN weaknesses w ON s.id = w.subject_id AND w.user_id = ?
                GROUP BY s.id, s.name
                ORDER BY weakness_count DESC
            """, (user_id,)).fetchall()
            
            # Get total weaknesses
            total = conn.execute("""
                SELECT COUNT(*) FROM weaknesses WHERE user_id = ?
            """, (user_id,)).fetchone()[0]
            
            return {
                'total_weaknesses': total,
                'by_subject': [dict(stat) for stat in stats]
            }
        except sqlite3.Error as e:
            print(f"Error getting weakness statistics: {e}")
            return {'total_weaknesses': 0, 'by_subject': []}
        finally:
            conn.close()
    
    @staticmethod
    def get_weakness_types():
        """Get all available weakness types"""
        return [
            'conceptual_understanding',
            'problem_solving',
            'memory_retention',
            'application_skills',
            'critical_thinking',
            'practical_skills',
            'theoretical_knowledge',
            'analysis_skills'
        ]