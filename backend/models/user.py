"""
User Model for AgriQuest v2.0

This module handles all user-related database operations including creation,
authentication, profile management, and role-based functionality. It supports
the three main user types: Admin, Teacher, and Student with unique identifiers
and comprehensive user management capabilities.

Classes:
    User: Main class for user operations

Methods:
    create_user: Create a new user with role-based user_id generation
    get_user_by_username: Retrieve user by username
    get_user_by_id: Retrieve user by database ID
    get_user_by_user_id: Retrieve user by role-based user_id (A001, T001, S001)
    get_all_users: Get all users in the system
    get_users_by_role: Get users filtered by role
    search_users: Search users by name, username, or email
    update_last_login: Update user's last login timestamp
    deactivate_user: Deactivate a user account
    activate_user: Activate a user account
    change_password: Change user password with verification
    update_profile: Update user profile information

Author: AgriQuest Development Team
Version: 2.0
"""

from ..config.database import get_db_connection
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

class User:
    @staticmethod
    def create_user(username, password, role='student', email=None, full_name=None, user_id=None):
        conn = get_db_connection()
        hashed_password = generate_password_hash(password)
        try:
            # Generate user_id if not provided
            if not user_id:
                # Get the next ID for the role
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM users WHERE role = ?", (role,))
                count = cursor.fetchone()[0]
                
                if role == 'admin':
                    user_id = f"A{count + 1:03d}"
                elif role == 'teacher':
                    user_id = f"T{count + 1:03d}"
                elif role == 'student':
                    user_id = f"S{count + 1:03d}"
                else:
                    user_id = f"U{count + 1:03d}"
            
            conn.execute("""
                INSERT INTO users (username, password, role, email, full_name, user_id, is_active, created_at) 
                VALUES (?, ?, ?, ?, ?, ?, 1, datetime('now'))
            """, (username, hashed_password, role, email, full_name or username, user_id))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
    
    @staticmethod
    def get_user_by_username(username):
        conn = get_db_connection()
        conn.row_factory = sqlite3.Row
        user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        conn.close()
        return dict(user) if user else None
    
    @staticmethod
    def get_user_by_id(user_id):
        conn = get_db_connection()
        conn.row_factory = sqlite3.Row
        user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        conn.close()
        return dict(user) if user else None
    
    @staticmethod
    def get_user_by_user_id(user_id):
        """Get user by user_id field (A001, T001, S001, etc.)"""
        conn = get_db_connection()
        conn.row_factory = sqlite3.Row
        user = conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchone()
        conn.close()
        return dict(user) if user else None
    
    @staticmethod
    def get_all_users():
        conn = get_db_connection()
        conn.row_factory = sqlite3.Row
        users = conn.execute("SELECT * FROM users ORDER BY created_at DESC").fetchall()
        conn.close()
        return [dict(user) for user in users]
    
    @staticmethod
    def get_users_by_role(role):
        """Get all users with a specific role"""
        conn = get_db_connection()
        conn.row_factory = sqlite3.Row
        users = conn.execute("SELECT * FROM users WHERE role = ? ORDER BY full_name", (role,)).fetchall()
        conn.close()
        return [dict(user) for user in users]
    
    @staticmethod
    def search_users(query, role=None):
        """Search users by username, full_name, or email"""
        conn = get_db_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if role:
            cursor.execute("""
                SELECT * FROM users 
                WHERE role = ? AND (username LIKE ? OR full_name LIKE ? OR email LIKE ?)
                ORDER BY full_name
            """, (role, f"%{query}%", f"%{query}%", f"%{query}%"))
        else:
            cursor.execute("""
                SELECT * FROM users 
                WHERE username LIKE ? OR full_name LIKE ? OR email LIKE ?
                ORDER BY full_name
            """, (f"%{query}%", f"%{query}%", f"%{query}%"))
        
        users = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return users
    
    @staticmethod
    def update_last_login(user_id):
        """Update last login timestamp"""
        conn = get_db_connection()
        conn.execute("UPDATE users SET last_login = datetime('now') WHERE id = ?", (user_id,))
        conn.commit()
        conn.close()
    
    @staticmethod
    def deactivate_user(user_id):
        """Deactivate a user account"""
        conn = get_db_connection()
        conn.execute("UPDATE users SET is_active = 0 WHERE id = ?", (user_id,))
        conn.commit()
        conn.close()
    
    @staticmethod
    def activate_user(user_id):
        """Activate a user account"""
        conn = get_db_connection()
        conn.execute("UPDATE users SET is_active = 1 WHERE id = ?", (user_id,))
        conn.commit()
        conn.close()
    
    @staticmethod
    def change_password(user_id, current_password, new_password):
        """Change user password with current password verification"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Get current password hash
            cursor.execute("SELECT password FROM users WHERE id = ?", (user_id,))
            result = cursor.fetchone()
            
            if not result:
                return False, "User not found"
            
            # Verify current password
            if not check_password_hash(result[0], current_password):
                return False, "Current password is incorrect"
            
            # Update password
            new_hash = generate_password_hash(new_password)
            cursor.execute("UPDATE users SET password = ? WHERE id = ?", (new_hash, user_id))
            conn.commit()
            
            return True, "Password changed successfully"
        except Exception as e:
            return False, f"Error: {e}"
        finally:
            conn.close()
    
    @staticmethod
    def update_user_role(user_id, role):
        conn = get_db_connection()
        conn.execute("UPDATE users SET role = ? WHERE id = ?", (role, user_id))
        conn.commit()
        conn.close()
    
    @staticmethod
    def delete_user(user_id):
        conn = get_db_connection()
        conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
        conn.close()
    
    @staticmethod
    def get_user_by_email(email):
        conn = get_db_connection()
        conn.row_factory = sqlite3.Row
        user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        conn.close()
        return dict(user) if user else None
    
    
    @staticmethod
    def update_password(user_id, new_password):
        conn = get_db_connection()
        hashed_password = generate_password_hash(new_password)
        conn.execute("UPDATE users SET password = ? WHERE id = ?", (hashed_password, user_id))
        conn.commit()
        conn.close()
        return True
    
    @staticmethod
    def update_profile(user_id, full_name=None, email=None, profile_picture=None):
        conn = get_db_connection()
        try:
            updates = []
            params = []
            
            if full_name is not None:
                updates.append("full_name = ?")
                params.append(full_name)
            
            if email is not None:
                updates.append("email = ?")
                params.append(email)
                
            
            if profile_picture is not None:
                updates.append("profile_picture = ?")
                params.append(profile_picture)
            
            if updates:
                params.append(user_id)
                query = f"UPDATE users SET {', '.join(updates)} WHERE id = ?"
                conn.execute(query, params)
                conn.commit()
                return True
            return False
        except Exception as e:
            print(f"Error updating profile: {e}")
            return False
        finally:
            conn.close()
    
    @staticmethod
    def get_profile_picture_path(user_id):
        """Get the profile picture path for a user"""
        conn = get_db_connection()
        try:
            user = conn.execute("SELECT profile_picture FROM users WHERE id = ?", (user_id,)).fetchone()
            return user['profile_picture'] if user else None
        except Exception as e:
            print(f"Error getting profile picture: {e}")
            return None
        finally:
            conn.close()
    
    @staticmethod
    def delete_profile_picture(user_id):
        """Delete profile picture from database"""
        conn = get_db_connection()
        try:
            conn.execute("UPDATE users SET profile_picture = NULL WHERE id = ?", (user_id,))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error deleting profile picture: {e}")
            return False
        finally:
            conn.close()
    
    @staticmethod
    def get_user_performance(user_id):
        """Get user's quiz performance for students"""
        conn = get_db_connection()
        try:
            # Get all quiz results for the user
            results = conn.execute("""
                SELECT r.*, q.title as quiz_title, q.difficulty_level, s.name as subject_name
                FROM results r
                JOIN quizzes q ON r.quiz_id = q.id
                JOIN subjects s ON q.subject_id = s.id
                WHERE r.user_id = ?
                ORDER BY r.timestamp DESC
            """, (user_id,)).fetchall()
            
            # Calculate performance statistics
            total_quizzes = len(results)
            total_score = sum(result['score'] for result in results)
            total_questions = sum(result['total_questions'] for result in results)
            avg_score = (total_score / total_questions * 100) if total_questions > 0 else 0
            
            passed_quizzes = sum(1 for result in results if (result['score'] / result['total_questions']) >= 0.8)
            pass_rate = (passed_quizzes / total_quizzes * 100) if total_quizzes > 0 else 0
            
            return {
                'total_quizzes': total_quizzes,
                'total_score': total_score,
                'total_questions': total_questions,
                'avg_score': round(avg_score, 1),
                'passed_quizzes': passed_quizzes,
                'pass_rate': round(pass_rate, 1),
                'recent_results': [dict(result) for result in results[:5]]  # Last 5 results
            }
        except Exception as e:
            print(f"Error getting user performance: {e}")
            return None
        finally:
            conn.close()
    
    @staticmethod
    def get_teacher_quizzes(user_id):
        """Get teacher's created quizzes"""
        conn = get_db_connection()
        try:
            quizzes = conn.execute("""
                SELECT q.*, s.name as subject_name,
                       COUNT(r.id) as total_attempts,
                       AVG(r.score) as avg_score
                FROM quizzes q
                JOIN subjects s ON q.subject_id = s.id
                LEFT JOIN results r ON q.id = r.quiz_id
                WHERE q.creator_id = ?
                GROUP BY q.id
                ORDER BY q.created_at DESC
            """, (user_id,)).fetchall()
            
            return [dict(quiz) for quiz in quizzes]
        except Exception as e:
            print(f"Error getting teacher quizzes: {e}")
            return []
        finally:
            conn.close()
    
    @staticmethod
    def get_recent_activities(user_id, role):
        """Get recent activities based on user role"""
        conn = get_db_connection()
        try:
            activities = []
            
            if role == 'student':
                # Get recent quiz attempts
                results = conn.execute("""
                    SELECT r.timestamp, r.score, r.total_questions, q.title as quiz_title, s.name as subject_name
                    FROM results r
                    JOIN quizzes q ON r.quiz_id = q.id
                    JOIN subjects s ON q.subject_id = s.id
                    WHERE r.user_id = ?
                    ORDER BY r.timestamp DESC
                    LIMIT 10
                """, (user_id,)).fetchall()
                
                for result in results:
                    percentage = (result['score'] / result['total_questions']) * 100
                    activities.append({
                        'type': 'quiz_completed',
                        'timestamp': result['timestamp'],
                        'description': f"Completed quiz '{result['quiz_title']}' in {result['subject_name']}",
                        'details': f"Score: {result['score']}/{result['total_questions']} ({percentage:.1f}%)",
                        'icon': 'fas fa-question-circle',
                        'color': 'success' if percentage >= 80 else 'warning' if percentage >= 60 else 'danger'
                    })
            
            elif role == 'teacher':
                # Get recent quiz creations and student attempts
                quiz_creations = conn.execute("""
                    SELECT q.created_at, q.title, s.name as subject_name
                    FROM quizzes q
                    JOIN subjects s ON q.subject_id = s.id
                    WHERE q.creator_id = ?
                    ORDER BY q.created_at DESC
                    LIMIT 5
                """, (user_id,)).fetchall()
                
                for quiz in quiz_creations:
                    activities.append({
                        'type': 'quiz_created',
                        'timestamp': quiz['created_at'],
                        'description': f"Created quiz '{quiz['title']}' in {quiz['subject_name']}",
                        'details': "New quiz available for students",
                        'icon': 'fas fa-plus-circle',
                        'color': 'primary'
                    })
                
                # Get recent student attempts on teacher's quizzes
                recent_attempts = conn.execute("""
                    SELECT r.timestamp, r.score, r.total_questions, q.title as quiz_title, u.username as student_name
                    FROM results r
                    JOIN quizzes q ON r.quiz_id = q.id
                    JOIN users u ON r.user_id = u.id
                    WHERE q.creator_id = ?
                    ORDER BY r.timestamp DESC
                    LIMIT 5
                """, (user_id,)).fetchall()
                
                for attempt in recent_attempts:
                    percentage = (attempt['score'] / attempt['total_questions']) * 100
                    activities.append({
                        'type': 'student_attempt',
                        'timestamp': attempt['timestamp'],
                        'description': f"{attempt['student_name']} completed '{attempt['quiz_title']}'",
                        'details': f"Score: {attempt['score']}/{attempt['total_questions']} ({percentage:.1f}%)",
                        'icon': 'fas fa-user-graduate',
                        'color': 'info'
                    })
            
            # Sort all activities by timestamp
            activities.sort(key=lambda x: x['timestamp'], reverse=True)
            return activities[:10]  # Return last 10 activities
            
        except Exception as e:
            print(f"Error getting recent activities: {e}")
            return []
        finally:
            conn.close()
