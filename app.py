import os
import logging

from flask import Flask
from datetime import datetime

from config import get_config
from handlers import register_error_handlers, LogManager


def create_app(config_class=None):
    """Application factory"""
    app = Flask(__name__)
    
    # Loading configuration
    if config_class is None:
        config_class = get_config()
    
    app.config.from_object(config_class)
    
    # Initializing configuration
    config_class.init_app(app)

    # Setting up logging
    LogManager.setup_logging(app)
    
    # Register Blueprints
    register_blueprints(app)
    
    # Registration of error handlers
    register_error_handlers(app)
    
    # Registration of CLI commands
    register_commands(app)
    
    # Registration of context processors
    register_context_processors(app)
    
    return app


def register_blueprints(app):
    """Registration of all Blueprints"""
    from routes.api import api_bp
    from routes.website import site_bp
    
    app.register_blueprint(site_bp)
    app.register_blueprint(api_bp, url_prefix='/api')


def register_commands(app):
    """Registration of CLI commands"""
    
    @app.cli.command('init-db')
    def init_db_command():
        """Database initialization (if added in the future)"""
        app.logger.info('Database initialization would happen here')
    
    @app.cli.command('clear-uploads')
    def clear_uploads_command():
        """Clearing the uploads folder"""
        import shutil
        import os
        
        uploads_dir = app.config['UPLOAD_FOLDER']
        if os.path.exists(uploads_dir):
            shutil.rmtree(uploads_dir)
            os.makedirs(uploads_dir)
            app.logger.info('Uploads folder cleared')
        else:
            app.logger.info('Uploads folder does not exist')
    
    @app.cli.command('check-config')
    def check_config_command():
        """Checking the current configuration"""
        app.logger.info('Current configuration:')
        for key, value in app.config.items():
            if not key.startswith('_') and not callable(value):
                app.logger.info(f'  {key}: {value}')


def register_context_processors(app):
    """Registration of context processors"""
    
    @app.context_processor
    def utility_processor():
        """Adding utilities to the template context"""

        return {
            'app_name': app.config['APP_NAME'],
            'app_version': '1.0.0',
            'current_year': datetime.now().year,
            'max_file_size_mb': app.config['MAX_CONTENT_LENGTH'] // (1024 * 1024)
        }


app = create_app()


if __name__ == '__main__':
    app.run(
        host=os.environ.get('FLASK_HOST', '0.0.0.0'),
        port=int(os.environ.get('FLASK_PORT', 5000)),
        debug=app.config['DEBUG']
    )

