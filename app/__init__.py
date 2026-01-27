"""
Flask application factory
"""
from flask import Flask, jsonify
from app.config import config
from app.extensions import init_extensions
from app.routes import register_blueprints
from flask_jwt_extended.exceptions import JWTExtendedException
from werkzeug.exceptions import HTTPException


def create_app(config_name='default'):
    """
    Application factory pattern
    
    Args:
        config_name: Configuration name (development, production, testing)
    
    Returns:
        Flask application instance
    """
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    init_extensions(app)
    
    # Register blueprints
    register_blueprints(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register CLI commands
    register_cli_commands(app)
    
    # Health check endpoint
    @app.route('/')
    def index():
        return jsonify({
            'message': 'Gym Management System API',
            'version': '1.0.0',
            'status': 'running',
            'docs': '/test'
        })
    
    @app.route('/health')
    def health():
        return jsonify({'status': 'healthy'})
    
    return app


def register_error_handlers(app):
    """Register error handlers"""
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 'Resource not found'
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500
    
    @app.errorhandler(JWTExtendedException)
    def handle_jwt_exception(error):
        return jsonify({
            'success': False,
            'error': str(error)
        }), 401
    
    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        return jsonify({
            'success': False,
            'error': error.description
        }), error.code
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        app.logger.error(f'Unhandled exception: {str(error)}')
        return jsonify({
            'success': False,
            'error': 'An unexpected error occurred'
        }), 500


def register_cli_commands(app):
    """Register Flask CLI commands"""
    
    @app.cli.command('init-db')
    def init_db():
        """Initialize database"""
        from app.extensions import db
        db.create_all()
        print('✅ Database initialized successfully!')
    
    @app.cli.command('seed-db')
    def seed_db():
        """Seed database with test data"""
        from seed import seed_database
        seed_database()
        print('✅ Database seeded successfully!')
    
    @app.cli.command('reset-db')
    def reset_db():
        """Reset database (drop all tables and recreate)"""
        from app.extensions import db
        
        response = input('⚠️  This will delete all data. Are you sure? (yes/no): ')
        if response.lower() == 'yes':
            db.drop_all()
            db.create_all()
            print('✅ Database reset successfully!')
        else:
            print('❌ Operation cancelled.')
