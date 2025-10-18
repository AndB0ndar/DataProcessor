import json
import logging

from flask import current_app
from datetime import datetime, timedelta
from logging.handlers import RotatingFileHandler


class LogManager:
    """System Logs Manager"""
    
    @staticmethod
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
    
    @staticmethod
    def get_application_logs(limit=100, level=None):
        """Getting application logs"""
        # TODO
        # In the real application, there will be a reading from the log file
        # while we return the stub.
        return []
    
    @staticmethod
    def log_processing_event(task_id, event_type, message, details=None):
        """Logging of processing events"""
        logger = logging.getLogger('DataProcessor.Processing')
        
        log_data = {
            'timestamp': datetime.now().isoformat(),
            'task_id': task_id,
            'event_type': event_type,
            'message': message,
            'details': details
        }
        
        if event_type == 'error':
            logger.error(json.dumps(log_data, ensure_ascii=False))
        elif event_type == 'warning':
            logger.warning(json.dumps(log_data, ensure_ascii=False))
        else:
            logger.info(json.dumps(log_data, ensure_ascii=False))
    
    @staticmethod
    def get_system_metrics():
        """Getting system metrics"""
        import psutil
        import os
        
        return {
            'cpu_percent': psutil.cpu_percent(),
            'memory_usage': psutil.virtual_memory().percent,
            'disk_usage': psutil.disk_usage('/').percent,
            'active_tasks': len([t for t in TaskManager._tasks.values() if t['status'] == 'processing']),
            'upload_folder_size': LogManager._get_folder_size(current_app.config['UPLOAD_FOLDER']),
            'results_folder_size': LogManager._get_folder_size(current_app.config['RESULTS_FOLDER'])
        }
    
    @staticmethod
    def _get_folder_size(folder_path):
        """Getting the folder size"""
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(folder_path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                total_size += os.path.getsize(filepath)
        return total_size

