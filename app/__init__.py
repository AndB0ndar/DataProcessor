import os
import logging

from datetime import datetime

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from app.config import get_config
from app.handlers import register_error_handlers


db = SQLAlchemy()


def create_app():
    config_class = get_config()

    app = Flask(
        __name__,
        static_url_path=f"{config_class.APPLICATION_ROOT}/static",
        static_folder=os.path.join(config_class.ROOT_PATH, 'static')
    )
    app.config.from_object(config_class)
    
    db.init_app(app)

    setup_logging(app)
    
    register_blueprints(app)
    register_error_handlers(app)
    register_context_processors(app)
    
    # Initializing services
    from app.services.librelane_service import LibreLaneService
    LibreLaneService.init_service(app)

    return app


def register_blueprints(app):
    """Registration of all Blueprints"""
    from app.routes.auth import auth_bp
    from app.routes.api import api_bp
    from app.routes.website import site_bp
    
    root = app.config['APPLICATION_ROOT']
    app.register_blueprint(auth_bp, url_prefix=root)
    app.register_blueprint(site_bp, url_prefix=root)
    app.register_blueprint(api_bp, url_prefix=f"{root}/api")


def register_context_processors(app):
    """Registration of context processors"""
    
    @app.context_processor
    def utility_processor():
        """Adding utilities"""

        return {
            'app_name': app.config['APP_NAME'],
            'app_version': '1.0.0',
            'current_year': datetime.now().year,
            'max_file_size_mb': app.config['MAX_CONTENT_LENGTH'] // (1024 * 1024)
        }

    @app.context_processor
    def inject_active_run():
        """Adding current_run"""
        from flask import session
        if 'session_id' in session:
            from app.services.run_service import RunService
            current_run = RunService.get_last_run(session['session_id'])
            return dict(current_run=current_run)
        return dict(current_run=None)


def setup_logging(app):
    """Configuring the logging system"""
    logging.basicConfig(
        level=getattr(logging, app.config['LOG_LEVEL']),
        format=app.config['LOG_FORMAT']
    )

    if not app.config['DEBUG'] and not app.config['TESTING']:
        try:
            log_folder = app.config['LOG_FOLDER']
            if not os.path.exists(log_folder):
                os.makedirs(log_folder)

            file_handler = RotatingFileHandler(
                os.path.join(log_folder, 'flask.log'),
                maxBytes=10240,
                backupCount=10
            )
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s [%(levelname)s] %(message)s (in %(pathname)s:%(lineno)d)'
            ))
            file_handler.setLevel(getattr(logging, app.config['LOG_LEVEL']))

            # Add to Flask's app logger specifically
            app.logger.addHandler(file_handler)

        except Exception as e:
            logging.error(f"Failed to setup file logging: {str(e)}")

