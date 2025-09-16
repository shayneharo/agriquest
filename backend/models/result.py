"""
Result Model
Handles result and analytics database operations
"""

from ..config.database import get_db_connection
import sqlite3

class Result:
    @staticmethod
    def save_result(user_id, quiz_id, score, total_questions):
        conn = get_db_connection()
        conn.execute('''INSERT INTO results (user_id, quiz_id, score, total_questions)
                        VALUES (?, ?, ?, ?)''', (user_id, quiz_id, score, total_questions))
        conn.commit()
        conn.close()
    
    @staticmethod
    def get_user_results(user_id):
        conn = get_db_connection()
        results = conn.execute('''SELECT results.*, quizzes.title as quiz_title, subjects.name as subject_name
                                  FROM results 
                                  JOIN quizzes ON results.quiz_id = quizzes.id
                                  JOIN subjects ON quizzes.subject_id = subjects.id
                                  WHERE user_id = ? ORDER BY timestamp DESC''', (user_id,)).fetchall()
        conn.close()
        return results
    
    @staticmethod
    def get_user_quiz_result(user_id, quiz_id):
        conn = get_db_connection()
        result = conn.execute('''SELECT results.*, quizzes.title as quiz_title, subjects.name as subject_name
                                FROM results 
                                JOIN quizzes ON results.quiz_id = quizzes.id
                                JOIN subjects ON quizzes.subject_id = subjects.id
                                WHERE user_id = ? AND quiz_id = ?''', (user_id, quiz_id)).fetchone()
        conn.close()
        return result
    
    @staticmethod
    def get_user_analytics(user_id):
        conn = get_db_connection()
        # Overall performance
        overall = conn.execute('''SELECT 
                                    COUNT(*) as total_quizzes,
                                    AVG(score * 100.0 / total_questions) as average_score,
                                    MAX(score * 100.0 / total_questions) as best_score,
                                    MIN(score * 100.0 / total_questions) as worst_score
                                  FROM results WHERE user_id = ?''', (user_id,)).fetchone()
        
        # Performance by subject
        by_subject = conn.execute('''SELECT 
                                       subjects.name as subject_name,
                                       COUNT(*) as quiz_count,
                                       AVG(score * 100.0 / total_questions) as average_score
                                     FROM results 
                                     JOIN quizzes ON results.quiz_id = quizzes.id
                                     JOIN subjects ON quizzes.subject_id = subjects.id
                                     WHERE user_id = ?
                                     GROUP BY subjects.id, subjects.name
                                     ORDER BY average_score ASC''', (user_id,)).fetchall()
        
        # Recent performance trend
        recent_trend = conn.execute('''SELECT 
                                         DATE(timestamp) as date,
                                         AVG(score * 100.0 / total_questions) as daily_average
                                       FROM results 
                                       WHERE user_id = ? 
                                       AND timestamp >= datetime('now', '-30 days')
                                       GROUP BY DATE(timestamp)
                                       ORDER BY date DESC''', (user_id,)).fetchall()
        
        conn.close()
        return {
            'overall': overall,
            'by_subject': by_subject,
            'recent_trend': recent_trend
        }
    
    @staticmethod
    def get_weak_areas(user_id):
        conn = get_db_connection()
        weak_areas = conn.execute('''SELECT 
                                       subjects.name as subject_name,
                                       AVG(score * 100.0 / total_questions) as average_score,
                                       COUNT(*) as quiz_count
                                     FROM results 
                                     JOIN quizzes ON results.quiz_id = quizzes.id
                                     JOIN subjects ON quizzes.subject_id = subjects.id
                                     WHERE user_id = ?
                                     GROUP BY subjects.id, subjects.name
                                     HAVING average_score < 70
                                     ORDER BY average_score ASC''', (user_id,)).fetchall()
        conn.close()
        return weak_areas
    
    @staticmethod
    def get_all_results_for_teachers():
        conn = get_db_connection()
        results = conn.execute('''SELECT 
                                   results.*, 
                                   quizzes.title as quiz_title, 
                                   subjects.name as subject_name,
                                   users.username as student_name
                                 FROM results 
                                 JOIN quizzes ON results.quiz_id = quizzes.id
                                 JOIN subjects ON quizzes.subject_id = subjects.id
                                 JOIN users ON results.user_id = users.id
                                 ORDER BY results.timestamp DESC''').fetchall()
        conn.close()
        return results
    
    @staticmethod
    def get_quiz_results(quiz_id):
        conn = get_db_connection()
        results = conn.execute('''SELECT results.*, users.username as student_name
                                 FROM results 
                                 JOIN users ON results.user_id = users.id
                                 WHERE quiz_id = ?
                                 ORDER BY results.timestamp DESC''', (quiz_id,)).fetchall()
        conn.close()
        return [dict(result) for result in results]
    
    @staticmethod
    def get_detailed_quiz_results(quiz_id):
        conn = get_db_connection()
        results = conn.execute('''SELECT 
                                   results.*, 
                                   users.username as student_name,
                                   users.email as student_email
                                 FROM results 
                                 JOIN users ON results.user_id = users.id
                                 WHERE quiz_id = ?
                                 ORDER BY results.timestamp DESC''', (quiz_id,)).fetchall()
        conn.close()
        return [dict(result) for result in results]
    
    @staticmethod
    def get_result_by_id(result_id):
        conn = get_db_connection()
        result = conn.execute("SELECT * FROM results WHERE id = ?", (result_id,)).fetchone()
        conn.close()
        return dict(result) if result else None
    
    @staticmethod
    def delete_result(result_id):
        conn = get_db_connection()
        conn.execute("DELETE FROM results WHERE id = ?", (result_id,))
        conn.commit()
        conn.close()
