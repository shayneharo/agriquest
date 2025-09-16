"""
Subject Teacher Model for AgriQuest v2.0

This module handles all subject-teacher relationship database operations including
inviting teachers to subjects, accepting/rejecting invitations, and managing
subject assignments.

Classes:
    SubjectTeacher: Main class for subject-teacher operations

Methods:
    invite_teacher: Invite a teacher to manage a subject
    accept_invitation: Teacher accepts an invitation
    reject_invitation: Teacher rejects an invitation
    get_teacher_subjects: Get subjects assigned to a teacher
    get_subject_teachers: Get teachers assigned to a subject
    remove_teacher: Remove teacher from subject
    get_pending_invitations: Get pending invitations for a teacher

Author: AgriQuest Development Team
Version: 2.0
"""

from ..config.database import get_db_connection
import sqlite3

class SubjectTeacher:
    @staticmethod
    def invite_teacher(teacher_id, subject_id):
        """Invite a teacher to manage a subject"""
        conn = get_db_connection()
        try:
            # Check if invitation already exists
            existing = conn.execute("""
                SELECT id FROM subject_teachers 
                WHERE teacher_id = ? AND subject_id = ?
            """, (teacher_id, subject_id)).fetchone()
            
            if existing:
                return False, "Teacher already invited to this subject"
            
            conn.execute("""
                INSERT INTO subject_teachers (teacher_id, subject_id, status, invited_at) 
                VALUES (?, ?, 'pending', datetime('now'))
            """, (teacher_id, subject_id))
            conn.commit()
            return True, "Invitation sent successfully"
        except sqlite3.Error as e:
            print(f"Error inviting teacher: {e}")
            return False, f"Error: {e}"
        finally:
            conn.close()
    
    @staticmethod
    def accept_invitation(teacher_id, subject_id):
        """Teacher accepts an invitation to manage a subject"""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE subject_teachers 
                SET status = 'accepted', accepted_at = datetime('now')
                WHERE teacher_id = ? AND subject_id = ? AND status = 'pending'
            """, (teacher_id, subject_id))
            conn.commit()
            
            if cursor.rowcount > 0:
                return True, "Invitation accepted successfully"
            else:
                return False, "No pending invitation found"
        except sqlite3.Error as e:
            print(f"Error accepting invitation: {e}")
            return False, f"Error: {e}"
        finally:
            conn.close()
    
    @staticmethod
    def reject_invitation(teacher_id, subject_id):
        """Teacher rejects an invitation to manage a subject"""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE subject_teachers 
                SET status = 'rejected'
                WHERE teacher_id = ? AND subject_id = ? AND status = 'pending'
            """, (teacher_id, subject_id))
            conn.commit()
            
            if cursor.rowcount > 0:
                return True, "Invitation rejected successfully"
            else:
                return False, "No pending invitation found"
        except sqlite3.Error as e:
            print(f"Error rejecting invitation: {e}")
            return False, f"Error: {e}"
        finally:
            conn.close()
    
    @staticmethod
    def get_teacher_subjects(teacher_id):
        """Get subjects assigned to a teacher"""
        conn = get_db_connection()
        try:
            subjects = conn.execute("""
                SELECT s.*, st.status, st.accepted_at
                FROM subjects s
                JOIN subject_teachers st ON s.id = st.subject_id
                WHERE st.teacher_id = ? AND st.status = 'accepted'
                ORDER BY s.name
            """, (teacher_id,)).fetchall()
            return [dict(subject) for subject in subjects]
        except sqlite3.Error as e:
            print(f"Error getting teacher subjects: {e}")
            return []
        finally:
            conn.close()
    
    @staticmethod
    def get_subject_teachers(subject_id):
        """Get teachers assigned to a subject"""
        conn = get_db_connection()
        try:
            teachers = conn.execute("""
                SELECT u.*, st.status, st.accepted_at
                FROM users u
                JOIN subject_teachers st ON u.id = st.teacher_id
                WHERE st.subject_id = ?
                ORDER BY st.status, u.full_name
            """, (subject_id,)).fetchall()
            return [dict(teacher) for teacher in teachers]
        except sqlite3.Error as e:
            print(f"Error getting subject teachers: {e}")
            return []
        finally:
            conn.close()
    
    @staticmethod
    def remove_teacher(teacher_id, subject_id):
        """Remove teacher from subject"""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM subject_teachers 
                WHERE teacher_id = ? AND subject_id = ?
            """, (teacher_id, subject_id))
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Error removing teacher: {e}")
            return False
        finally:
            conn.close()
    
    @staticmethod
    def get_pending_invitations(teacher_id):
        """Get pending invitations for a teacher"""
        conn = get_db_connection()
        try:
            invitations = conn.execute("""
                SELECT s.*, st.invited_at
                FROM subjects s
                JOIN subject_teachers st ON s.id = st.subject_id
                WHERE st.teacher_id = ? AND st.status = 'pending'
                ORDER BY st.invited_at DESC
            """, (teacher_id,)).fetchall()
            return [dict(invitation) for invitation in invitations]
        except sqlite3.Error as e:
            print(f"Error getting pending invitations: {e}")
            return []
        finally:
            conn.close()
    
    @staticmethod
    def get_all_invitations():
        """Get all invitations (for admin)"""
        conn = get_db_connection()
        try:
            invitations = conn.execute("""
                SELECT st.*, u.username as teacher_name, u.full_name as teacher_full_name,
                       s.name as subject_name
                FROM subject_teachers st
                JOIN users u ON st.teacher_id = u.id
                JOIN subjects s ON st.subject_id = s.id
                ORDER BY st.invited_at DESC
            """).fetchall()
            return [dict(invitation) for invitation in invitations]
        except sqlite3.Error as e:
            print(f"Error getting all invitations: {e}")
            return []
        finally:
            conn.close()