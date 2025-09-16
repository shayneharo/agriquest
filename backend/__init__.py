"""
AgriQuest Backend Package v2.0
Agricultural Learning Platform - Backend Services

This is the main backend package for AgriQuest v2.0, a comprehensive
role-based agricultural learning platform. It provides a complete
Flask-based web application with support for three user types:
Admin/Adviser, Subject Teacher, and Student.

Features:
    - Role-based access control system
    - User management and authentication
    - Subject and teacher management
    - Student enrollment system
    - Quiz creation and management
    - Notification system
    - Weakness tracking and analysis
    - Profile management
    - Real-time notifications

Architecture:
    - Flask application factory pattern
    - Blueprint-based modular structure
    - SQLite database with migration support
    - MVC (Model-View-Controller) architecture
    - RESTful API endpoints

Author: AgriQuest Development Team
Version: 2.0
"""

from flask import Flask
from .config.database import init_db

def create_app():
    """Application factory pattern"""
    app = Flask(__name__, 
                template_folder='../frontend/templates',
                static_folder='../frontend/static')
    
    # Configuration
    app.secret_key = 'your_secret_key_here'  # Change this in production!
    
    # Initialize database
    init_db()
    
    # Register blueprints
    from .controllers.auth_controller import auth_bp
    from .controllers.quiz_controller import quiz_bp
    from .controllers.analytics_controller import analytics_bp
    from .controllers.classes_controller import classes_bp
    
    # Register main blueprints
    from .controllers.admin_controller import admin_bp
    from .controllers.teacher_controller import teacher_bp
    from .controllers.student_controller import student_bp
    from .controllers.profile_controller import profile_bp
    
    # Register API blueprints
    from .api.auth_api import auth_api
    from .api.admin_api import admin_api
    from .api.teacher_api import teacher_api
    from .api.student_api import student_api
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(quiz_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(classes_bp)
    
    # Register main blueprints
    app.register_blueprint(admin_bp)
    app.register_blueprint(teacher_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(profile_bp)
    
    # Register API blueprints
    app.register_blueprint(auth_api)
    app.register_blueprint(admin_api)
    app.register_blueprint(teacher_api)
    app.register_blueprint(student_api)
    
    return app
