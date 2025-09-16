"""
Quiz Model
Handles quiz-related database operations
"""

from ..config.database import get_db_connection
import sqlite3

class Quiz:
    @staticmethod
    def create_quiz(title, subject_id, creator_id, description="", difficulty_level="beginner", time_limit=0, deadline=None):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get subject name for the subject column
        subject_name = cursor.execute("SELECT name FROM subjects WHERE id = ?", (subject_id,)).fetchone()
        if not subject_name:
            raise ValueError(f"Subject with id {subject_id} not found")
        
        cursor.execute("INSERT INTO quizzes (title, subject, subject_id, creator_id, description, difficulty_level, time_limit, deadline) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                      (title, subject_name[0], subject_id, creator_id, description, difficulty_level, time_limit, deadline))
        quiz_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return quiz_id
    
    @staticmethod
    def add_question(quiz_id, question_text, options, correct_option, explanation=""):
        conn = get_db_connection()
        conn.execute('''INSERT INTO questions 
                        (quiz_id, question_text, option1, option2, option3, option4, correct_option, explanation)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                    (quiz_id, question_text, options[0], options[1], options[2], options[3], correct_option, explanation))
        conn.commit()
        conn.close()
    
    @staticmethod
    def get_all_quizzes():
        conn = get_db_connection()
        quizzes = conn.execute('''SELECT quizzes.*, users.username as creator_name, subjects.name as subject_name
                                  FROM quizzes 
                                  JOIN users ON quizzes.creator_id = users.id
                                  JOIN subjects ON quizzes.subject_id = subjects.id
                                  ORDER BY quizzes.created_at DESC''').fetchall()
        conn.close()
        return quizzes
    
    @staticmethod
    def get_quizzes_by_subject(subject_id):
        conn = get_db_connection()
        quizzes = conn.execute('''SELECT quizzes.*, users.username as creator_name, subjects.name as subject_name
                                  FROM quizzes 
                                  JOIN users ON quizzes.creator_id = users.id
                                  JOIN subjects ON quizzes.subject_id = subjects.id
                                  WHERE quizzes.subject_id = ?
                                  ORDER BY quizzes.created_at DESC''', (subject_id,)).fetchall()
        conn.close()
        return quizzes
    
    @staticmethod
    def get_quizzes_for_classes(class_ids):
        """Get quizzes for specific classes (for now, return all quizzes since we don't have class-quiz mapping yet)"""
        if not class_ids:
            return []
        
        conn = get_db_connection()
        # For now, return all quizzes since we don't have a direct class-quiz relationship
        # In a real implementation, you'd have a classes_quizzes table
        quizzes = conn.execute('''SELECT quizzes.*, users.username as creator_name, subjects.name as subject_name
                                  FROM quizzes 
                                  JOIN users ON quizzes.creator_id = users.id
                                  JOIN subjects ON quizzes.subject_id = subjects.id
                                  ORDER BY quizzes.created_at DESC''').fetchall()
        conn.close()
        return quizzes
    
    @staticmethod
    def get_quiz_with_questions(quiz_id):
        conn = get_db_connection()
        quiz = conn.execute("SELECT * FROM quizzes WHERE id = ?", (quiz_id,)).fetchone()
        questions = conn.execute("SELECT * FROM questions WHERE quiz_id = ?", (quiz_id,)).fetchall()
        conn.close()
        return quiz, questions
    
    @staticmethod
    def get_quiz_by_id(quiz_id):
        conn = get_db_connection()
        quiz = conn.execute("SELECT * FROM quizzes WHERE id = ?", (quiz_id,)).fetchone()
        conn.close()
        return dict(quiz) if quiz else None
    
    @staticmethod
    def get_questions_by_quiz_id(quiz_id):
        conn = get_db_connection()
        questions = conn.execute("SELECT * FROM questions WHERE quiz_id = ?", (quiz_id,)).fetchall()
        conn.close()
        return [dict(question) for question in questions]
    
    @staticmethod
    def update_quiz(quiz_id, title, description, difficulty_level, time_limit, deadline=None):
        conn = get_db_connection()
        conn.execute('''UPDATE quizzes 
                        SET title = ?, description = ?, difficulty_level = ?, time_limit = ?, deadline = ?
                        WHERE id = ?''',
                    (title, description, difficulty_level, time_limit, deadline, quiz_id))
        conn.commit()
        conn.close()
    
    @staticmethod
    def delete_quiz(quiz_id):
        conn = get_db_connection()
        # Delete questions first (foreign key constraint)
        conn.execute("DELETE FROM questions WHERE quiz_id = ?", (quiz_id,))
        # Delete results
        conn.execute("DELETE FROM results WHERE quiz_id = ?", (quiz_id,))
        # Delete quiz
        conn.execute("DELETE FROM quizzes WHERE id = ?", (quiz_id,))
        conn.commit()
        conn.close()
    
    @staticmethod
    def get_question_by_id(question_id):
        conn = get_db_connection()
        question = conn.execute("SELECT * FROM questions WHERE id = ?", (question_id,)).fetchone()
        conn.close()
        return dict(question) if question else None
    
    @staticmethod
    def update_question(question_id, question_text, options, correct_option, explanation=""):
        conn = get_db_connection()
        conn.execute('''UPDATE questions 
                        SET question_text = ?, option1 = ?, option2 = ?, option3 = ?, option4 = ?, 
                            correct_option = ?, explanation = ?
                        WHERE id = ?''',
                    (question_text, options[0], options[1], options[2], options[3], 
                     correct_option, explanation, question_id))
        conn.commit()
        conn.close()
    
    @staticmethod
    def delete_question(question_id):
        conn = get_db_connection()
        conn.execute("DELETE FROM questions WHERE id = ?", (question_id,))
        conn.commit()
        conn.close()
    
    @staticmethod
    def is_quiz_open(quiz_id):
        """Check if a quiz is still open based on deadline"""
        conn = get_db_connection()
        quiz = conn.execute("SELECT deadline FROM quizzes WHERE id = ?", (quiz_id,)).fetchone()
        conn.close()
        
        if not quiz or not quiz[0]:  # No deadline set
            return True
        
        from datetime import datetime
        deadline = datetime.fromisoformat(quiz[0])
        return datetime.now() < deadline
    
    @staticmethod
    def get_quizzes_by_creator(creator_id):
        """Get all quizzes created by a specific user"""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT q.id, q.title, q.subject_id, q.creator_id, q.description,
                       q.difficulty_level, q.time_limit, q.created_at, q.deadline,
                       s.name as subject_name
                FROM quizzes q
                LEFT JOIN subjects s ON q.subject_id = s.id
                WHERE q.creator_id = ?
                ORDER BY q.created_at DESC
            """, (creator_id,))
            quizzes = cursor.fetchall()
            return [dict(row) for row in quizzes]
        except Exception as e:
            print(f"Error getting quizzes by creator: {e}")
            return []
        finally:
            conn.close()
