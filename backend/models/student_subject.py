"""
Student Subject Model for AgriQuest v2.0

This module handles all student-subject relationship database operations including
student enrollment requests, teacher approval/rejection, and managing student
access to subjects.

Classes:
    StudentSubject: Main class for student-subject operations

Methods:
    request_enrollment: Student requests to join a subject
    approve_enrollment: Teacher approves student enrollment
    reject_enrollment: Teacher rejects student enrollment
    get_student_subjects: Get subjects enrolled by a student
    get_subject_students: Get students enrolled in a subject
    remove_student: Remove student from subject
    get_pending_requests: Get pending enrollment requests for a teacher

Author: AgriQuest Development Team
Version: 2.0
"""

from ..config.database import get_db_connection
import sqlite3

class StudentSubject:
    @staticmethod
    def request_enrollment(student_id, subject_id):
        """Student requests to join a subject"""
        conn = get_db_connection()
        try:
            # Check if request already exists
            existing = conn.execute("""
                SELECT id FROM student_subjects 
                WHERE student_id = ? AND subject_id = ?
            """, (student_id, subject_id)).fetchone()
            
            if existing:
                return False, "Enrollment request already exists"
            
            conn.execute("""
                INSERT INTO student_subjects (student_id, subject_id, status, requested_at) 
                VALUES (?, ?, 'pending', datetime('now'))
            """, (student_id, subject_id))
            conn.commit()
            return True, "Enrollment request submitted successfully"
        except sqlite3.Error as e:
            print(f"Error requesting enrollment: {e}")
            return False, f"Error: {e}"
        finally:
            conn.close()
    
    @staticmethod
    def approve_enrollment(student_id, subject_id):
        """Teacher approves student enrollment"""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE student_subjects 
                SET status = 'approved', approved_at = datetime('now')
                WHERE student_id = ? AND subject_id = ? AND status = 'pending'
            """, (student_id, subject_id))
            conn.commit()
            
            if cursor.rowcount > 0:
                return True, "Enrollment approved successfully"
            else:
                return False, "No pending enrollment request found"
        except sqlite3.Error as e:
            print(f"Error approving enrollment: {e}")
            return False, f"Error: {e}"
        finally:
            conn.close()
    
    @staticmethod
    def reject_enrollment(student_id, subject_id):
        """Teacher rejects student enrollment"""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE student_subjects 
                SET status = 'rejected'
                WHERE student_id = ? AND subject_id = ? AND status = 'pending'
            """, (student_id, subject_id))
            conn.commit()
            
            if cursor.rowcount > 0:
                return True, "Enrollment rejected successfully"
            else:
                return False, "No pending enrollment request found"
        except sqlite3.Error as e:
            print(f"Error rejecting enrollment: {e}")
            return False, f"Error: {e}"
        finally:
            conn.close()
    
    @staticmethod
    def get_student_subjects(student_id):
        """Get subjects enrolled by a student"""
        conn = get_db_connection()
        try:
            subjects = conn.execute("""
                SELECT s.*, ss.status, ss.approved_at
                FROM subjects s
                JOIN student_subjects ss ON s.id = ss.subject_id
                WHERE ss.student_id = ? AND ss.status = 'approved'
                ORDER BY s.name
            """, (student_id,)).fetchall()
            return [dict(subject) for subject in subjects]
        except sqlite3.Error as e:
            print(f"Error getting student subjects: {e}")
            return []
        finally:
            conn.close()
    
    @staticmethod
    def get_subject_students(subject_id):
        """Get students enrolled in a subject"""
        conn = get_db_connection()
        try:
            students = conn.execute("""
                SELECT u.*, ss.status, ss.approved_at
                FROM users u
                JOIN student_subjects ss ON u.id = ss.student_id
                WHERE ss.subject_id = ?
                ORDER BY ss.status, u.full_name
            """, (subject_id,)).fetchall()
            return [dict(student) for student in students]
        except sqlite3.Error as e:
            print(f"Error getting subject students: {e}")
            return []
        finally:
            conn.close()
    
    @staticmethod
    def remove_student(student_id, subject_id):
        """Remove student from subject"""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM student_subjects 
                WHERE student_id = ? AND subject_id = ?
            """, (student_id, subject_id))
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Error removing student: {e}")
            return False
        finally:
            conn.close()
    
    @staticmethod
    def get_pending_requests(teacher_id):
        """Get pending enrollment requests for subjects managed by a teacher"""
        conn = get_db_connection()
        try:
            requests = conn.execute("""
                SELECT ss.*, u.username as student_name, u.full_name as student_full_name,
                       s.name as subject_name
                FROM student_subjects ss
                JOIN users u ON ss.student_id = u.id
                JOIN subjects s ON ss.subject_id = s.id
                JOIN subject_teachers st ON s.id = st.subject_id
                WHERE st.teacher_id = ? AND st.status = 'accepted' AND ss.status = 'pending'
                ORDER BY ss.requested_at DESC
            """, (teacher_id,)).fetchall()
            return [dict(request) for request in requests]
        except sqlite3.Error as e:
            print(f"Error getting pending requests: {e}")
            return []
        finally:
            conn.close()
    
    @staticmethod
    def get_all_requests():
        """Get all enrollment requests (for admin)"""
        conn = get_db_connection()
        try:
            requests = conn.execute("""
                SELECT ss.*, u.username as student_name, u.full_name as student_full_name,
                       s.name as subject_name
                FROM student_subjects ss
                JOIN users u ON ss.student_id = u.id
                JOIN subjects s ON ss.subject_id = s.id
                ORDER BY ss.requested_at DESC
            """).fetchall()
            return [dict(request) for request in requests]
        except sqlite3.Error as e:
            print(f"Error getting all requests: {e}")
            return []
        finally:
            conn.close()
    
    @staticmethod
    def is_student_enrolled(student_id, subject_id):
        """Check if student is enrolled in a subject"""
        conn = get_db_connection()
        try:
            result = conn.execute("""
                SELECT id FROM student_subjects 
                WHERE student_id = ? AND subject_id = ? AND status = 'approved'
            """, (student_id, subject_id)).fetchone()
            return result is not None
        except sqlite3.Error as e:
            print(f"Error checking enrollment: {e}")
            return False
        finally:
            conn.close()