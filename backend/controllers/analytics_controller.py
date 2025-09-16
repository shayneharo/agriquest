"""
Analytics Controller
Handles performance analytics and reporting
"""

from flask import Blueprint, render_template, session, flash, request
from ..models.result import Result
from ..models.quiz import Quiz
from ..models.subject import Subject
from ..models.class_model import Class as ClassModel
from .auth_controller import login_required
from ..config.database import get_db_connection

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/analytics')
@login_required
def analytics():
    user_role = session.get('role', 'student')
    
    if user_role == 'teacher':
        # Teacher analytics - monitor student performance
        return get_teacher_analytics()
    else:
        # Student analytics - personal performance
        analytics = Result.get_user_analytics(session['user_id'])
        weak_areas = Result.get_weak_areas(session['user_id'])
        return render_template('analytics.html', analytics=analytics, weak_areas=weak_areas, user_role=user_role)

def get_teacher_analytics():
    """Get comprehensive analytics for teachers to monitor student performance"""
    conn = get_db_connection()
    
    # Get all students' results
    all_results = Result.get_all_results_for_teachers()
    
    # Overall statistics
    total_quizzes_taken = len(all_results)
    total_students = len(set(result['user_id'] for result in all_results))
    
    # Calculate average performance
    if all_results:
        avg_score = sum(result['score'] * 100.0 / result['total_questions'] for result in all_results) / len(all_results)
    else:
        avg_score = 0
    
    # Performance by subject
    subject_performance = conn.execute('''SELECT 
                                           subjects.name as subject_name,
                                           COUNT(*) as quiz_count,
                                           AVG(score * 100.0 / total_questions) as average_score,
                                           COUNT(DISTINCT results.user_id) as student_count
                                         FROM results 
                                         JOIN quizzes ON results.quiz_id = quizzes.id
                                         JOIN subjects ON quizzes.subject_id = subjects.id
                                         GROUP BY subjects.id, subjects.name
                                         ORDER BY average_score DESC''').fetchall()
    
    # Top performing students
    top_students = conn.execute('''SELECT 
                                    users.username as student_name,
                                    COUNT(*) as quiz_count,
                                    AVG(score * 100.0 / total_questions) as average_score
                                  FROM results 
                                  JOIN users ON results.user_id = users.id
                                  GROUP BY users.id, users.username
                                  HAVING quiz_count >= 1
                                  ORDER BY average_score DESC
                                  LIMIT 10''').fetchall()
    
    # Students needing attention (low performance)
    struggling_students = conn.execute('''SELECT 
                                           users.username as student_name,
                                           COUNT(*) as quiz_count,
                                           AVG(score * 100.0 / total_questions) as average_score
                                         FROM results 
                                         JOIN users ON results.user_id = users.id
                                         GROUP BY users.id, users.username
                                         HAVING quiz_count >= 1 AND average_score < 70
                                         ORDER BY average_score ASC''').fetchall()
    
    # Recent activity (last 7 days)
    recent_activity = conn.execute('''SELECT 
                                       results.*,
                                       quizzes.title as quiz_title,
                                       subjects.name as subject_name,
                                       users.username as student_name
                                     FROM results 
                                     JOIN quizzes ON results.quiz_id = quizzes.id
                                     JOIN subjects ON quizzes.subject_id = subjects.id
                                     JOIN users ON results.user_id = users.id
                                     WHERE results.timestamp >= datetime('now', '-7 days')
                                     ORDER BY results.timestamp DESC
                                     LIMIT 20''').fetchall()
    
    # Quiz popularity (most taken quizzes)
    quiz_popularity = conn.execute('''SELECT 
                                       quizzes.title as quiz_title,
                                       subjects.name as subject_name,
                                       COUNT(*) as attempt_count,
                                       AVG(score * 100.0 / total_questions) as average_score
                                     FROM results 
                                     JOIN quizzes ON results.quiz_id = quizzes.id
                                     JOIN subjects ON quizzes.subject_id = subjects.id
                                     GROUP BY quizzes.id, quizzes.title
                                     ORDER BY attempt_count DESC
                                     LIMIT 10''').fetchall()
    
    conn.close()
    
    # Prepare data for template
    teacher_analytics = {
        'overview': {
            'total_quizzes_taken': total_quizzes_taken,
            'total_students': total_students,
            'average_score': round(avg_score, 2)
        },
        'subject_performance': subject_performance,
        'top_students': top_students,
        'struggling_students': struggling_students,
        'recent_activity': recent_activity,
        'quiz_popularity': quiz_popularity
    }
    
    return render_template('teacher_analytics.html', analytics=teacher_analytics, user_role='teacher')
