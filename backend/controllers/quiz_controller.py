"""
Quiz Controller
Handles quiz creation, taking, and management
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from ..models.user import User
from ..models.quiz import Quiz
from ..models.subject import Subject
from ..models.result import Result
from ..models.class_model import Class as ClassModel
from .auth_controller import login_required

quiz_bp = Blueprint('quiz', __name__)

@quiz_bp.route('/')
def public_home():
    """Public home page - redirects to login if not authenticated"""
    if 'user_id' in session:
        # User is logged in, show home page
        user_role = session.get('role', 'student')
        return render_template('home.html', user_role=user_role)
    else:
        # User is not logged in, redirect to login
        return redirect(url_for('auth.login'))

@quiz_bp.route('/home')
@login_required
def home():
    """Home page - redirect to role-specific dashboard"""
    user_role = session.get('role')
    
    if user_role == 'admin':
        return redirect(url_for('admin.dashboard'))
    elif user_role == 'teacher':
        return redirect(url_for('teacher.dashboard'))
    elif user_role == 'student':
        return redirect(url_for('student.dashboard'))
    else:
        # Fallback to old home page for unknown roles
        user_id = session['user_id']
        user = User.get_user_by_id(user_id)
        user_full_name = user.get('full_name') if user else session.get('username', 'User')
        
        return render_template('home.html', 
                             user_role=user_role, 
                             user_full_name=user_full_name)

@quiz_bp.route('/subjects')
@login_required
def subjects():
    # Check if user is a student and enrolled in any class
    if session.get('role') == 'student':
        from ..models.class_model import Class
        student_classes = Class.get_classes_for_student(session['user_id'])
        if not student_classes:
            flash('You must enroll in a class before accessing subjects. Please enroll in a class first.', 'error')
            return redirect(url_for('classes.my_classes'))
    
    subjects = Subject.get_all_subjects()
    return render_template('subjects.html', subjects=subjects)

@quiz_bp.route('/subject/<int:subject_id>')
@login_required
def subject_quizzes(subject_id):
    # Check if user is a student and enrolled in any class
    if session.get('role') == 'student':
        from ..models.class_model import Class
        student_classes = Class.get_classes_for_student(session['user_id'])
        if not student_classes:
            flash('You must enroll in a class before accessing quizzes. Please enroll in a class first.', 'error')
            return redirect(url_for('classes.my_classes'))
    
    subject = Subject.get_subject_by_id(subject_id)
    quizzes = Quiz.get_quizzes_by_subject(subject_id)
    from datetime import datetime
    return render_template('subject_quizzes.html', subject=subject, quizzes=quizzes, now=datetime.now())

@quiz_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_quiz_short():
    """Short route for /quiz/create that redirects to create_quiz"""
    return redirect(url_for('quiz.create_quiz'))

@quiz_bp.route('/create_quiz', methods=['GET', 'POST'])
@login_required
def create_quiz():
    if session.get('role') not in ['teacher', 'admin']:
        flash('Only teachers and admins can create quizzes', 'error')
        return redirect(url_for('quiz.home'))
    
    if request.method == 'POST':
        title = request.form['title']
        subject_id = int(request.form['subject_id'])
        description = request.form.get('description', '')
        difficulty_level = request.form.get('difficulty_level', 'beginner')
        time_limit = int(request.form.get('time_limit', 10))  # Default to 10 minutes
        deadline = request.form.get('deadline', '') or None  # Get deadline, empty string becomes None
        
        # Convert minutes to seconds for storage
        time_limit_seconds = time_limit * 60
        
        # Get teacher's name
        teacher = User.get_user_by_id(session['user_id'])
        teacher_name = teacher['username'] if teacher else 'Unknown Teacher'
        
        # Add time limit and teacher name to description
        if time_limit > 0 and 'minute' not in description.lower():
            if description:
                description += f" (Time limit: {time_limit} minutes)"
            else:
                description = f"Time limit: {time_limit} minutes"
        
        # Add teacher name to description
        if 'Created by' not in description:
            if description:
                description += f" | Created by: {teacher_name}"
            else:
                description = f"Created by: {teacher_name}"
        
        quiz_id = Quiz.create_quiz(title, subject_id, session['user_id'], 
                                  description, difficulty_level, time_limit_seconds, deadline)
        
        # Process questions
        question_count = int(request.form['question_count'])
        for i in range(1, question_count + 1):
            question_text = request.form[f'question_{i}']
            options = [
                request.form[f'question_{i}_option1'],
                request.form[f'question_{i}_option2'],
                request.form[f'question_{i}_option3'],
                request.form[f'question_{i}_option4']
            ]
            correct_option = int(request.form[f'question_{i}_correct'])
            
            Quiz.add_question(quiz_id, question_text, options, correct_option)
        
        flash('Quiz created successfully!', 'success')
        return redirect(url_for('quiz.home'))
    
    subjects = Subject.get_all_subjects()
    return render_template('create_quiz.html', subjects=subjects)

@quiz_bp.route('/take_quiz/<int:quiz_id>', methods=['GET', 'POST'])
@login_required
def take_quiz(quiz_id):
    quiz, questions = Quiz.get_quiz_with_questions(quiz_id)
    
    if not quiz:
        flash('Quiz not found', 'error')
        return redirect(url_for('quiz.home'))
    
    # Check if user is a student and enrolled in any class
    if session.get('role') == 'student':
        from ..models.class_model import Class
        student_classes = Class.get_classes_for_student(session['user_id'])
        if not student_classes:
            flash('You must enroll in a class before taking quizzes. Please enroll in a class first.', 'error')
            return redirect(url_for('classes.my_classes'))
    
    # Check if quiz is still open
    if not Quiz.is_quiz_open(quiz_id):
        flash('This quiz has closed. The deadline has passed.', 'error')
        return redirect(url_for('quiz.home'))
    
    # Check if user already took this quiz
    existing_result = Result.get_user_quiz_result(session['user_id'], quiz_id)
    if existing_result:
        # User already took this quiz, show results instead
        flash('You have already completed this quiz. Here are your results:', 'info')
        return redirect(url_for('quiz.view_quiz_result', quiz_id=quiz_id))
    
    # Convert Row objects to dictionaries for JSON serialization
    questions = [dict(question) for question in questions]
    quiz = dict(quiz)
    
    if request.method == 'POST':
        # Handle quiz submission
        if 'submit_quiz' in request.form:
            score = 0
            detailed_results = []
            
            for question in questions:
                user_answer = request.form.get(f'question_{question["id"]}')
                is_correct = user_answer and int(user_answer) == question['correct_option']
                
                if is_correct:
                    score += 1
                
                # Store detailed result for each question
                detailed_results.append({
                    'question': question,
                    'user_answer': int(user_answer) if user_answer else None,
                    'correct_answer': question['correct_option'],
                    'is_correct': is_correct,
                    'explanation': question['explanation'] if 'explanation' in question.keys() else ''
                })
            
            # Save overall result
            Result.save_result(session['user_id'], quiz_id, score, len(questions))
            
            # Store detailed results in session for display
            session['quiz_results'] = {
                'quiz': quiz,
                'score': score,
                'total_questions': len(questions),
                'detailed_results': detailed_results
            }
            
            return redirect(url_for('quiz.quiz_results'))
        
        # Handle individual question navigation
        elif 'next_question' in request.form:
            current_question = int(request.form.get('current_question', 1))
            next_question = current_question + 1
            
            # Save current answer
            if current_question <= len(questions):
                user_answer = request.form.get(f'question_{questions[current_question-1]["id"]}')
                if user_answer:
                    if 'quiz_answers' not in session:
                        session['quiz_answers'] = {}
                    session['quiz_answers'][questions[current_question-1]["id"]] = int(user_answer)
            
            if next_question > len(questions):
                return redirect(url_for('quiz.quiz_results'))
            else:
                return render_template('take_quiz_enhanced.html', 
                                    quiz=quiz, 
                                    questions=questions, 
                                    current_question=next_question,
                                    total_questions=len(questions))
        
        # Handle previous question
        elif 'prev_question' in request.form:
            current_question = int(request.form.get('current_question', 1))
            prev_question = max(1, current_question - 1)
            
            # Save current answer
            if current_question <= len(questions):
                user_answer = request.form.get(f'question_{questions[current_question-1]["id"]}')
                if user_answer:
                    if 'quiz_answers' not in session:
                        session['quiz_answers'] = {}
                    session['quiz_answers'][questions[current_question-1]["id"]] = int(user_answer)
            
            return render_template('take_quiz_enhanced.html', 
                                quiz=quiz, 
                                questions=questions, 
                                current_question=prev_question,
                                total_questions=len(questions))
        
        # Handle flagging questions
        elif 'flag_question' in request.form:
            current_question = int(request.form.get('current_question', 1))
            question_id = questions[current_question-1]["id"]
            
            if 'flagged_questions' not in session:
                session['flagged_questions'] = []
            
            if question_id in session['flagged_questions']:
                session['flagged_questions'].remove(question_id)
            else:
                session['flagged_questions'].append(question_id)
            
            return render_template('take_quiz_enhanced.html', 
                                quiz=quiz, 
                                questions=questions, 
                                current_question=current_question,
                                total_questions=len(questions))
    
    # Initialize quiz session
    session['quiz_answers'] = {}
    session['flagged_questions'] = []
    
    # Set time limit to 10 minutes (600 seconds) if not already set
    if 'quiz_time_left' not in session:
        session['quiz_time_left'] = 600
    
    return render_template('take_quiz_enhanced.html', 
                        quiz=quiz, 
                        questions=questions, 
                        current_question=1,
                        total_questions=len(questions))

@quiz_bp.route('/quiz_results')
@login_required
def quiz_results():
    """Display detailed quiz results with explanations"""
    if 'quiz_results' not in session:
        flash('No quiz results found', 'error')
        return redirect(url_for('quiz.home'))
    
    results = session['quiz_results']
    session.pop('quiz_results', None)  # Clear from session after displaying
    
    return render_template('quiz_results.html', results=results)

@quiz_bp.route('/view_quiz_result/<int:quiz_id>')
@login_required
def view_quiz_result(quiz_id):
    """Display existing quiz result for a specific quiz"""
    result = Result.get_user_quiz_result(session['user_id'], quiz_id)
    
    if not result:
        flash('No result found for this quiz', 'error')
        return redirect(url_for('quiz.home'))
    
    # Get quiz details and questions for detailed display
    quiz, questions = Quiz.get_quiz_with_questions(quiz_id)
    if not quiz:
        flash('Quiz not found', 'error')
        return redirect(url_for('quiz.home'))
    
    # Convert to dictionaries
    quiz = dict(quiz)
    questions = [dict(question) for question in questions]
    
    # Create detailed results structure similar to quiz_results
    detailed_results = []
    for question in questions:
        # For existing results, we don't have individual question answers stored
        # So we'll show the question without user's specific answer
        detailed_results.append({
            'question': question,
            'user_answer': None,  # We don't store individual answers
            'correct_answer': question['correct_option'],
            'is_correct': None,  # Can't determine without stored answers
            'explanation': question['explanation'] if 'explanation' in question.keys() else ''
        })
    
    results = {
        'quiz': quiz,
        'score': result['score'],
        'total_questions': result['total_questions'],
        'detailed_results': detailed_results,
        'timestamp': result['timestamp']
    }
    
    return render_template('quiz_results.html', results=results)

@quiz_bp.route('/results')
@login_required
def view_results():
    results = Result.get_user_results(session['user_id'])
    analytics = Result.get_user_analytics(session['user_id'])
    weak_areas = Result.get_weak_areas(session['user_id'])
    return render_template('results.html', results=results, analytics=analytics, weak_areas=weak_areas)

@quiz_bp.route('/view_quizzes/<int:subject_id>')
@quiz_bp.route('/view_quizzes/<int:subject_id>/<int:class_id>')
@login_required
def view_quizzes_for_subject(subject_id, class_id=None):
    """View all quizzes for a specific subject"""
    if session['role'] != 'teacher':
        flash('Access denied. Teacher role required.', 'error')
        return redirect(url_for('quiz.home'))
    
    subject = Subject.get_subject_by_id(subject_id)
    if not subject:
        flash('Subject not found', 'error')
        return redirect(url_for('quiz.home'))
    
    quizzes = Quiz.get_quizzes_by_subject(subject_id)
    
    # Convert Row objects to dictionaries and add total_questions to each quiz
    quizzes = [dict(quiz) for quiz in quizzes]
    for quiz in quizzes:
        questions = Quiz.get_questions_by_quiz_id(quiz['id'])
        quiz['total_questions'] = len(questions)
    
    from datetime import datetime
    return render_template('view_quizzes.html', subject=subject, quizzes=quizzes, class_id=class_id, now=datetime.now())

@quiz_bp.route('/edit_quiz/<int:quiz_id>')
@login_required
def edit_quiz(quiz_id):
    """Edit an existing quiz"""
    if session['role'] != 'teacher':
        flash('Access denied. Teacher role required.', 'error')
        return redirect(url_for('quiz.home'))
    
    quiz = Quiz.get_quiz_by_id(quiz_id)
    if not quiz:
        flash('Quiz not found', 'error')
        return redirect(url_for('quiz.home'))
    
    questions = Quiz.get_questions_by_quiz_id(quiz_id)
    subjects = Subject.get_all_subjects()
    return render_template('edit_quiz.html', quiz=quiz, questions=questions, subjects=subjects)

@quiz_bp.route('/update_quiz/<int:quiz_id>', methods=['POST'])
@login_required
def update_quiz(quiz_id):
    """Update quiz details"""
    if session['role'] != 'teacher':
        flash('Access denied. Teacher role required.', 'error')
        return redirect(url_for('quiz.home'))
    
    quiz = Quiz.get_quiz_by_id(quiz_id)
    if not quiz:
        flash('Quiz not found', 'error')
        return redirect(url_for('quiz.home'))
    
    # Get subject_id before updating
    subject_id = quiz['subject_id']
    
    title = request.form.get('title')
    description = request.form.get('description')
    difficulty_level = request.form.get('difficulty_level')
    time_limit_minutes = int(request.form.get('time_limit', 10))
    deadline = request.form.get('deadline', '') or None  # Get deadline, empty string becomes None
    
    # Convert minutes to seconds for storage
    time_limit_seconds = time_limit_minutes * 60
    
    if not title:
        flash('Quiz title is required', 'error')
        return redirect(url_for('quiz.edit_quiz', quiz_id=quiz_id))
    
    # Get teacher's name
    teacher = User.get_user_by_id(session['user_id'])
    teacher_name = teacher['username'] if teacher else 'Unknown Teacher'
    
    # Add time limit and teacher name to description if not already present
    if time_limit_minutes > 0 and 'minute' not in description.lower():
        if description:
            description += f" (Time limit: {time_limit_minutes} minutes)"
        else:
            description = f"Time limit: {time_limit_minutes} minutes"
    
    # Add teacher name to description if not already present
    if 'Created by' not in description:
        if description:
            description += f" | Created by: {teacher_name}"
        else:
            description = f"Created by: {teacher_name}"
    
    # Update quiz
    print(f"Updating quiz {quiz_id}: title='{title}', description='{description}', difficulty='{difficulty_level}', time_limit={time_limit_seconds}s")
    Quiz.update_quiz(quiz_id, title, description, difficulty_level, time_limit_seconds, deadline)
    print(f"Quiz {quiz_id} updated successfully")
    flash('Quiz updated successfully!', 'success')
    return redirect(url_for('quiz.view_quizzes_for_subject', subject_id=subject_id))

@quiz_bp.route('/delete_quiz/<int:quiz_id>')
@login_required
def delete_quiz(quiz_id):
    """Delete a quiz"""
    if session['role'] != 'teacher':
        flash('Access denied. Teacher role required.', 'error')
        return redirect(url_for('quiz.home'))
    
    quiz = Quiz.get_quiz_by_id(quiz_id)
    if not quiz:
        flash('Quiz not found', 'error')
        return redirect(url_for('quiz.home'))
    
    subject_id = quiz['subject_id']
    Quiz.delete_quiz(quiz_id)
    flash('Quiz deleted successfully!', 'success')
    return redirect(url_for('quiz.view_quizzes_for_subject', subject_id=subject_id))

@quiz_bp.route('/quiz_analytics/<int:quiz_id>')
@login_required
def quiz_analytics(quiz_id):
    """View analytics for a specific quiz"""
    if session['role'] != 'teacher':
        flash('Access denied. Teacher role required.', 'error')
        return redirect(url_for('quiz.home'))
    
    quiz = Quiz.get_quiz_by_id(quiz_id)
    if not quiz:
        flash('Quiz not found', 'error')
        return redirect(url_for('quiz.home'))
    
    # Convert Row object to dictionary and get questions count for this quiz
    quiz = dict(quiz)
    questions = Quiz.get_questions_by_quiz_id(quiz_id)
    quiz['total_questions'] = len(questions)
    
    # Get quiz results
    results = Result.get_quiz_results(quiz_id)
    
    # Calculate analytics
    total_attempts = len(results)
    if total_attempts > 0:
        scores = [result['score'] for result in results]
        avg_score = sum(scores) / len(scores)
        max_score = max(scores)
        min_score = min(scores)
        
        # Calculate pass rate (80% or higher)
        pass_threshold = quiz['total_questions'] * 0.8
        passed = sum(1 for score in scores if score >= pass_threshold)
        pass_rate = (passed / total_attempts) * 100
    else:
        avg_score = 0
        max_score = 0
        min_score = 0
        pass_rate = 0
    
    return render_template('quiz_analytics.html', 
                         quiz=quiz, 
                         results=results,
                         total_attempts=total_attempts,
                         avg_score=avg_score,
                         max_score=max_score,
                         min_score=min_score,
                         pass_rate=pass_rate)

@quiz_bp.route('/student_performance/<int:quiz_id>')
@login_required
def student_performance(quiz_id):
    """View detailed student performance for a quiz"""
    if session['role'] != 'teacher':
        flash('Access denied. Teacher role required.', 'error')
        return redirect(url_for('quiz.home'))
    
    quiz = Quiz.get_quiz_by_id(quiz_id)
    if not quiz:
        flash('Quiz not found', 'error')
        return redirect(url_for('quiz.home'))
    
    # Convert Row object to dictionary and get questions for this quiz
    quiz = dict(quiz)
    questions = Quiz.get_questions_by_quiz_id(quiz_id)
    quiz['total_questions'] = len(questions)
    
    # Get detailed results with user information
    results = Result.get_detailed_quiz_results(quiz_id)
    
    return render_template('student_performance.html', 
                         quiz=quiz, 
                         results=results,
                         questions=questions)

@quiz_bp.route('/edit_question/<int:question_id>')
@login_required
def edit_question(question_id):
    """Edit a specific question"""
    if session['role'] != 'teacher':
        flash('Access denied. Teacher role required.', 'error')
        return redirect(url_for('quiz.home'))
    
    question = Quiz.get_question_by_id(question_id)
    if not question:
        flash('Question not found', 'error')
        return redirect(url_for('quiz.home'))
    
    quiz = Quiz.get_quiz_by_id(question['quiz_id'])
    return render_template('edit_question.html', question=question, quiz=quiz)

@quiz_bp.route('/update_question/<int:question_id>', methods=['POST'])
@login_required
def update_question(question_id):
    """Update a specific question"""
    if session['role'] != 'teacher':
        flash('Access denied. Teacher role required.', 'error')
        return redirect(url_for('quiz.home'))
    
    question = Quiz.get_question_by_id(question_id)
    if not question:
        flash('Question not found', 'error')
        return redirect(url_for('quiz.home'))
    
    question_text = request.form.get('question_text')
    option1 = request.form.get('option1')
    option2 = request.form.get('option2')
    option3 = request.form.get('option3')
    option4 = request.form.get('option4')
    correct_option = int(request.form.get('correct_option'))
    explanation = request.form.get('explanation', '')
    
    if not all([question_text, option1, option2, option3, option4]):
        flash('All fields are required', 'error')
        return redirect(url_for('quiz.edit_question', question_id=question_id))
    
    # Update question
    Quiz.update_question(question_id, question_text, [option1, option2, option3, option4], correct_option, explanation)
    flash('Question updated successfully!', 'success')
    return redirect(url_for('quiz.edit_quiz', quiz_id=question['quiz_id']))

@quiz_bp.route('/delete_question/<int:question_id>')
@login_required
def delete_question(question_id):
    """Delete a specific question"""
    if session['role'] != 'teacher':
        flash('Access denied. Teacher role required.', 'error')
        return redirect(url_for('quiz.home'))
    
    question = Quiz.get_question_by_id(question_id)
    if not question:
        flash('Question not found', 'error')
        return redirect(url_for('quiz.home'))
    
    quiz_id = question['quiz_id']
    Quiz.delete_question(question_id)
    flash('Question deleted successfully!', 'success')
    return redirect(url_for('quiz.edit_quiz', quiz_id=quiz_id))

@quiz_bp.route('/add_question/<int:quiz_id>', methods=['GET', 'POST'])
@login_required
def add_question(quiz_id):
    """Add a new question to an existing quiz"""
    if session['role'] != 'teacher':
        flash('Access denied. Teacher role required.', 'error')
        return redirect(url_for('quiz.home'))
    
    quiz = Quiz.get_quiz_by_id(quiz_id)
    if not quiz:
        flash('Quiz not found', 'error')
        return redirect(url_for('quiz.home'))
    
    if request.method == 'POST':
        question_text = request.form.get('question_text')
        option1 = request.form.get('option1')
        option2 = request.form.get('option2')
        option3 = request.form.get('option3')
        option4 = request.form.get('option4')
        correct_option = int(request.form.get('correct_option'))
        explanation = request.form.get('explanation', '')
        
        if not all([question_text, option1, option2, option3, option4]):
            flash('All fields are required', 'error')
            return redirect(url_for('quiz.add_question', quiz_id=quiz_id))
        
        # Add question
        Quiz.add_question(quiz_id, question_text, [option1, option2, option3, option4], correct_option, explanation)
        flash('Question added successfully!', 'success')
        return redirect(url_for('quiz.edit_quiz', quiz_id=quiz_id))
    
    return render_template('add_question.html', quiz=quiz)

@quiz_bp.route('/delete_student_result/<int:result_id>')
@login_required
def delete_student_result(result_id):
    """Delete a student's quiz result"""
    if session['role'] != 'teacher':
        flash('Access denied. Teacher role required.', 'error')
        return redirect(url_for('quiz.home'))
    
    result = Result.get_result_by_id(result_id)
    if not result:
        flash('Result not found', 'error')
        return redirect(url_for('quiz.home'))
    
    quiz_id = result['quiz_id']
    Result.delete_result(result_id)
    flash('Student result deleted successfully!', 'success')
    return redirect(url_for('quiz.student_performance', quiz_id=quiz_id))
