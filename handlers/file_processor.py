import os
import uuid
import json
import logging

from flask import current_app
from werkzeug.utils import secure_filename

from .errors import ProcessingError


logger = logging.getLogger(__name__)


class FileProcessor:
    """File operation handler"""
    
    @staticmethod
    def save_uploaded_file(file, file_id=None):
        """Saving the uploaded file"""
        try:
            if file_id is None:
                file_id = str(uuid.uuid4())
            
            filename = secure_filename(file.filename)
            file_path = os.path.join(
                current_app.config['UPLOAD_FOLDER'], 
                f"{file_id}_{filename}"
            )
            
            # Saving the file
            file.save(file_path)
            
            logger.info(f"File saved: {filename}, path: {file_path}")
            
            return {
                'file_id': file_id,
                'filename': filename,
                'file_path': file_path,
                'file_size': os.path.getsize(file_path)
            }
            
        except Exception as e:
            logger.error(f"File saving error: {str(e)}")
            raise ProcessingError('Error saving file')
    
    @staticmethod
    def read_json_file(file_path):
        """Reading a JSON file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error reading the JSON file {file_path}: {str(e)}")
            raise ProcessingError('Error reading the file')
    
    @staticmethod
    def delete_file(file_path):
        """Deleting a file"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"File deleted: {file_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"File deletion error {file_path}: {str(e)}")
            raise ProcessingError('File deletion error')
    
    @staticmethod
    def get_file_info(file_path):
        """Getting information about a file"""
        try:
            if not os.path.exists(file_path):
                return None
            
            return {
                'size': os.path.getsize(file_path),
                'modified_time': os.path.getmtime(file_path),
                'created_time': os.path.getctime(file_path)
            }
        except Exception as e:
            logger.error(f"Error getting information about the file {file_path}: {str(e)}")
            return None

class ResultFileManager:
    """Results File Manager"""
    
    @staticmethod
    def create_result_directory(task_id):
        """Creating a directory for results"""
        result_dir = os.path.join(current_app.config['RESULTS_FOLDER'], task_id)
        os.makedirs(result_dir, exist_ok=True)
        return result_dir
    
    @staticmethod
    def save_analysis_results(task_id, results):
        """Saving the analysis results"""
        try:
            result_dir = ResultFileManager.create_result_directory(task_id)
            result_file = os.path.join(result_dir, 'analysis_results.json')
            
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Analysis results saved: {result_file}")
            return result_file
            
        except Exception as e:
            logger.error(f"Error saving results: {str(e)}")
            raise ProcessingError('Error saving results')
    
    @staticmethod
    def cleanup_old_files(days=7):
        """Cleaning up old files"""
        import time
        from pathlib import Path
        
        current_time = time.time()
        cutoff = current_time - (days * 24 * 60 * 60)
        
        cleaned_files = []
        
        # Clearing uploads
        for folder in [current_app.config['UPLOAD_FOLDER'], current_app.config['RESULTS_FOLDER']]:
            if not os.path.exists(folder):
                continue
                
            for file_path in Path(folder).rglob('*'):
                if file_path.is_file() and file_path.stat().st_mtime < cutoff:
                    try:
                        file_path.unlink()
                        cleaned_files.append(str(file_path))
                    except Exception as e:
                        logger.error(f"Error deleting old file {file_path}: {str(e)}")
        
        logger.info(f"Cleared {len(cleaned_files)} old files")
        return cleaned_files

