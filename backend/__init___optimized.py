"""
Optimized AgriQuest Backend Package
Enhanced Flask application with production-ready features
"""

import os
import logging
from flask import Flask, request, g
from flask_session import Session
from werkzeug.middleware.proxy_fix import ProxyFix

from config.config import get_config
from config.database_optimized import db_manager
from config.cache import cache_manager, cache_stats

def create_app(config_name=None):
    """Enhanced application factory pattern"""
    
    # Get configuration
    config_class = get_config()
    if config_name:
        from config.config import config
        config_class = config.get(config_name, get_config())
    
    # Create Flask application
    app = Flask(__name__, 
                template_folder='../frontend/templates',
                static_folder='../frontend/static')
    
    # Load configuration
    app.config.from_object(config_class)
    config_class.init_app(app)
    
    # Configure logging
    _configure_logging(app)
    
    # Initialize extensions
    _init_extensions(app)
    
    # Register blueprints
    _register_blueprints(app)
    
    # Configure middleware
    _configure_middleware(app)
    
    # Register error handlers
    _register_error_handlers(app)
    
    # Register context processors
    _register_context_processors(app)
    
    # Register CLI commands
    _register_cli_commands(app)
    
    return app

def _configure_logging(app):
    """Configure application logging"""
    if not app.debug and not app.testing:
        # Production logging
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        file_handler = logging.FileHandler('logs/agriquest.log')
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
        app.logger.setLevel(logging.INFO)
        app.logger.info('AgriQuest startup')

def _init_extensions(app):
    """Initialize Flask extensions"""
    
    # Session management
    Session(app)
    
    # Database initialization
    # Database is automatically initialized when db_manager is created
    
    # Cache initialization
    # Cache is automatically initialized when cache_manager is created

def _register_blueprints(app):
    """Register Flask blueprints"""
    from controllers.auth_controller import auth_bp
    from controllers.quiz_controller import quiz_bp
    from controllers.admin_controller import admin_bp
    from controllers.analytics_controller import analytics_bp
    from controllers.profile_controller import profile_bp
    from controllers.classes_controller import classes_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(quiz_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(classes_bp)

def _configure_middleware(app):
    """Configure application middleware"""
    
    # Proxy fix for production deployment
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
    
    # Request logging middleware
    @app.before_request
    def log_request_info():
        g.start_time = time.time()
        app.logger.debug(f"Request: {request.method} {request.url}")
    
    @app.after_request
    def log_response_info(response):
        if hasattr(g, 'start_time'):
            duration = time.time() - g.start_time
            app.logger.debug(f"Response: {response.status_code} ({duration:.3f}s)")
        return response

def _register_error_handlers(app):
    """Register error handlers"""
    
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db_manager.cleanup_expired_data()  # Clean up on error
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('errors/403.html'), 403

def _register_context_processors(app):
    """Register template context processors"""
    
    @app.context_processor
    def inject_config():
        """Inject configuration into templates"""
        return {
            'app_name': 'AgriQuest',
            'app_version': '2.0.0',
            'cache_stats': cache_stats.get_stats()
        }
    
    @app.context_processor
    def inject_user():
        """Inject current user into templates"""
        from flask import session
        if 'user_id' in session:
            # Get user from cache or database
            from models.user import User
            user = User.get_user_by_id(session['user_id'])
            return {'current_user': user}
        return {'current_user': None}

def _register_cli_commands(app):
    """Register CLI commands"""
    
    @app.cli.command()
    def init_db():
        """Initialize database"""
        db_manager._init_database()
        print("Database initialized successfully")
    
    @app.cli.command()
    def clear_cache():
        """Clear application cache"""
        cache_manager.clear()
        print("Cache cleared successfully")
    
    @app.cli.command()
    def cache_stats():
        """Show cache statistics"""
        stats = cache_stats.get_stats()
        print(f"Cache Statistics:")
        print(f"  Hits: {stats['hits']}")
        print(f"  Misses: {stats['misses']}")
        print(f"  Hit Rate: {stats['hit_rate']:.2f}%")
        print(f"  Sets: {stats['sets']}")
        print(f"  Deletes: {stats['deletes']}")
    
    @app.cli.command()
    def cleanup():
        """Clean up expired data"""
        db_manager.cleanup_expired_data()
        print("Expired data cleaned up successfully")
    
    @app.cli.command()
    def performance_report():
        """Generate performance report"""
        query_stats = db_manager.get_query_stats()
        cache_stats_data = cache_stats.get_stats()
        
        print("Performance Report:")
        print("=" * 50)
        
        print("\nDatabase Query Statistics:")
        for query_hash, stats in query_stats.items():
            print(f"  Query: {stats['query'][:50]}...")
            print(f"    Count: {stats['count']}")
            print(f"    Average Time: {stats['avg_time']:.3f}s")
            print()
        
        print("Cache Statistics:")
        print(f"  Hit Rate: {cache_stats_data['hit_rate']:.2f}%")
        print(f"  Total Operations: {cache_stats_data['hits'] + cache_stats_data['misses']}")

# Health check endpoint
def create_health_check_app():
    """Create minimal app for health checks"""
    health_app = Flask(__name__)
    
    @health_app.route('/health')
    def health_check():
        """Health check endpoint"""
        try:
            # Check database connection
            with db_manager.get_connection() as conn:
                conn.execute('SELECT 1')
            
            # Check cache connection
            cache_manager.get('health_check')
            
            return {
                'status': 'healthy',
                'database': 'connected',
                'cache': 'connected',
                'version': '2.0.0'
            }, 200
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e)
            }, 500
    
    return health_app

# Import time module for middleware
import time
from flask import render_template

# Create the main application
app = create_app()

# Create health check application
health_app = create_health_check_app()

if __name__ == '__main__':
    # Development server
    app.run(host='0.0.0.0', port=5000, debug=True)

