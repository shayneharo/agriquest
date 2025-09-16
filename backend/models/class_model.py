"""
Class Model
Handles class-related database operations
"""

from ..config.database import get_db_connection

class Class:
    @staticmethod
    def get_all_classes():
        """Get all available classes"""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT c.id, c.name, c.description, c.created_at,
                       COUNT(tc.teacher_id) as teacher_count
                FROM classes c
                LEFT JOIN teacher_classes tc ON c.id = tc.class_id
                GROUP BY c.id, c.name, c.description, c.created_at
                ORDER BY c.name
            """)
            classes = cursor.fetchall()
            return [dict(row) for row in classes]
        except Exception as e:
            print(f"Error getting classes: {e}")
            return []
        finally:
            conn.close()
    
    @staticmethod
    def get_class_by_id(class_id):
        """Get a specific class by ID"""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT c.id, c.name, c.description, c.created_at,
                       COUNT(tc.teacher_id) as teacher_count
                FROM classes c
                LEFT JOIN teacher_classes tc ON c.id = tc.class_id
                WHERE c.id = ?
                GROUP BY c.id, c.name, c.description, c.created_at
            """, (class_id,))
            result = cursor.fetchone()
            return dict(result) if result else None
        except Exception as e:
            print(f"Error getting class: {e}")
            return None
        finally:
            conn.close()
    
    @staticmethod
    def get_classes_for_teacher(teacher_id):
        """Get all classes assigned to a specific teacher"""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT c.id, c.name, c.description, c.created_at,
                       tc.created_at as assigned_at
                FROM classes c
                JOIN teacher_classes tc ON c.id = tc.class_id
                WHERE tc.teacher_id = ?
                ORDER BY c.name
            """, (teacher_id,))
            classes = cursor.fetchall()
            return [dict(row) for row in classes]
        except Exception as e:
            print(f"Error getting teacher classes: {e}")
            return []
        finally:
            conn.close()
    
    @staticmethod
    def get_classes_for_student(student_id):
        """Get all classes a student is enrolled in (approved only)"""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT c.id, c.name, c.description, c.created_at,
                       sc.status, sc.approved_at
                FROM classes c
                JOIN student_classes sc ON c.id = sc.class_id
                WHERE sc.student_id = ? AND sc.status = 'approved'
                ORDER BY c.name
            """, (student_id,))
            classes = cursor.fetchall()
            return [dict(row) for row in classes]
        except Exception as e:
            print(f"Error getting student classes: {e}")
            return []
        finally:
            conn.close()
    
    @staticmethod
    def get_student_enrollment_status(student_id, class_id):
        """Get the enrollment status of a student for a specific class"""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT status, requested_at, approved_at
                FROM student_classes
                WHERE student_id = ? AND class_id = ?
            """, (student_id, class_id))
            result = cursor.fetchone()
            return dict(result) if result else None
        except Exception as e:
            print(f"Error getting enrollment status: {e}")
            return None
        finally:
            conn.close()
    
    @staticmethod
    def enroll_student(student_id, class_id):
        """Enroll a student in a class (status: pending)"""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO student_classes (student_id, class_id, status, requested_at)
                VALUES (?, ?, 'pending', CURRENT_TIMESTAMP)
            """, (student_id, class_id))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error enrolling student: {e}")
            return False
        finally:
            conn.close()
    
    @staticmethod
    def approve_student(student_id, class_id):
        """Approve a student's enrollment in a class"""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE student_classes
                SET status = 'approved', approved_at = CURRENT_TIMESTAMP
                WHERE student_id = ? AND class_id = ?
            """, (student_id, class_id))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error approving student: {e}")
            return False
        finally:
            conn.close()
    
    @staticmethod
    def reject_student(student_id, class_id):
        """Reject a student's enrollment in a class"""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM student_classes
                WHERE student_id = ? AND class_id = ?
            """, (student_id, class_id))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error rejecting student: {e}")
            return False
        finally:
            conn.close()
    
    @staticmethod
    def get_pending_enrollments_for_class(class_id):
        """Get all pending enrollment requests for a specific class"""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT sc.id, sc.student_id, sc.requested_at,
                       u.username, u.email, u.created_at as user_created_at
                FROM student_classes sc
                JOIN users u ON sc.student_id = u.id
                WHERE sc.class_id = ? AND sc.status = 'pending'
                ORDER BY sc.requested_at
            """, (class_id,))
            enrollments = cursor.fetchall()
            return [dict(row) for row in enrollments]
        except Exception as e:
            print(f"Error getting pending enrollments: {e}")
            return []
        finally:
            conn.close()
    
    @staticmethod
    def is_teacher_of_class(teacher_id, class_id):
        """Check if a teacher is assigned to a specific class"""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) FROM teacher_classes
                WHERE teacher_id = ? AND class_id = ?
            """, (teacher_id, class_id))
            count = cursor.fetchone()[0]
            return count > 0
        except Exception as e:
            print(f"Error checking teacher assignment: {e}")
            return False
        finally:
            conn.close()
    
    @staticmethod
    def get_class_teachers(class_id):
        """Get all teachers assigned to a specific class"""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT u.id, u.username, u.email, tc.created_at as assigned_at
                FROM users u
                JOIN teacher_classes tc ON u.id = tc.teacher_id
                WHERE tc.class_id = ?
                ORDER BY u.username
            """, (class_id,))
            teachers = cursor.fetchall()
            return [dict(row) for row in teachers]
        except Exception as e:
            print(f"Error getting class teachers: {e}")
            return []
        finally:
            conn.close()
    
    @staticmethod
    def get_pending_enrollments():
        """Get all pending enrollment requests across all classes"""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT sc.id, sc.student_id, sc.class_id, sc.requested_at,
                       u.username, u.email, u.full_name,
                       c.name as class_name, c.description as class_description
                FROM student_classes sc
                JOIN users u ON sc.student_id = u.id
                JOIN classes c ON sc.class_id = c.id
                WHERE sc.status = 'pending'
                ORDER BY sc.requested_at DESC
            """)
            enrollments = cursor.fetchall()
            return [dict(row) for row in enrollments]
        except Exception as e:
            print(f"Error getting pending enrollments: {e}")
            return []
        finally:
            conn.close()
    
    @staticmethod
    def get_students_in_class(class_id):
        """Get all students enrolled in a specific class"""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT u.id, u.username, u.email, u.full_name,
                       sc.status, sc.approved_at, sc.enrolled_at
                FROM users u
                JOIN student_classes sc ON u.id = sc.student_id
                WHERE sc.class_id = ? AND sc.status = 'approved'
                ORDER BY u.username
            """, (class_id,))
            students = cursor.fetchall()
            return [dict(row) for row in students]
        except Exception as e:
            print(f"Error getting students in class: {e}")
            return []
        finally:
            conn.close()
