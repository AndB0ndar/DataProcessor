import os
import json
import uuid
import logging
import random

from datetime import datetime
from werkzeug.utils import secure_filename
from flask import Blueprint, request, jsonify, current_app

from handlers import (
    JSONValidator, FileProcessor, TaskManager, LogManager,
    ValidationError, ProcessingError
)


api_bp = Blueprint('api', __name__)

logger = logging.getLogger(__name__)


@api_bp.route('/upload', methods=['POST'])
def api_upload():
    """API for uploading a JSON file"""
    if 'file' not in request.files:
        raise ValidationError('File not found')
    
    file = request.files['file']
    
    # File validation
    JSONValidator.validate_file_upload(file)
    
    try:
        # Reading and parsing JSON
        file_content = file.read().decode('utf-8')
        json_data = json.loads(file_content)
        
        JSONValidator.validate_json_structure(json_data)
        JSONValidator.validate_json_content(json_data)
        
        # Saving the file
        file_info = FileProcessor.save_uploaded_file(file)
        
        # Creating a processing task
        task_id = TaskManager.create_task(file_info['file_path'])
        TaskManager.start_processing(task_id)
        
        # Event logging
        LogManager.log_processing_event(
            task_id, 
            'file_uploaded',
            f' File uploaded: {file_info["filename"]}',
            {'records_count': len(json_data['data']), 'file_size': file_info['file_size']}
        )
        
        return jsonify({
            'success': True,
            'message': 'The file has been uploaded and verified successfully',
            'task_id': task_id,
            'filename': file_info['filename'],
            'file_size': file_info['file_size'],
            'records_count': len(json_data['data'])
        })
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {str(e)}")
        raise ValidationError(f'JSON parsing error: {str(e)}')
    except (ValidationError, ProcessingError):
        raise
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        raise ProcessingError('Internal server error processing file')


@api_bp.route('/start_processing', methods=['POST'])
def api_start_processing():
    """API for starting data processing"""
    data = request.get_json()
    task_id = data.get('task_id')
    
    if not task_id:
        raise ValidationError('Issue ID not specified')
    
    # Here will be the logic for starting processing
    logger.info(f"Processing started for task_id: {task_id}")
    
    return jsonify({
        'success': True,
        'message': 'Data processing started',
        'task_id': task_id,
        'status_url': '/status',
        'timeout': current_app.config['PROCESSING_TIMEOUT']
    })


@api_bp.route('/processing_status/<task_id>')
def api_processing_status(task_id):
    """API for getting the processing status"""
    task_status = TaskManager.get_task_status(task_id)

    if not task_status:
        raise ValidationError('Task not found')

    return jsonify(task_status)


@api_bp.route('/results')
def api_results():
    """API for getting a list of results"""
    # Simulation of results data
    sample_results = [
        {
            'id': '2024-01-15_10-23-15',
            'name': '2024-01-15_10-23-15',
            'date': '2024-01-15 10:23:15',
            'status': 'completed',
            'metrics': {
                'records': 1000,
                'time': '00:02:30',
                'accuracy': '98.5%',
                'size': '2.4 MB'
            },
            'files': [
                {'name': 'report.pdf', 'size': '1.2 MB', 'type': 'pdf'},
                {'name': 'data_analysis.json', 'size': '0.8 MB', 'type': 'json'},
                {'name': 'visualization.png', 'size': '0.4 MB', 'type': 'image'}
            ]
        }
    ]
    
    return jsonify({'results': sample_results})


@api_bp.route('/logs')
def api_logs():
    """API for getting logs"""
    # Log simulation
    levels = ['info', 'warning', 'error', 'debug']
    messages = [
        'Data Integrity check',
        'Optimizing memory usage',
        'Caching intermediate results',
        'Exporting data to an external system',
        'Cleaning temporary files'
    ]
    
    logs = []
    for i in range(20):
        level = random.choice(levels)
        message = random.choice(messages)
        timestamp = f"10:{random.randint(20,30)}:{random.randint(10,59)}"
        logs.append({
            'timestamp': timestamp,
            'level': level,
            'message': message,
            'details': f' Details for {message.lower()} '
        })
    
    return jsonify({'logs': logs})


@api_bp.route('/config')
def api_config():
    """API for getting configuration information (for development only)"""
    if current_app.config['DEBUG']:
        return jsonify({
            'config': {
                'max_file_size': current_app.config['MAX_CONTENT_LENGTH'],
                'allowed_extensions': list(current_app.config['ALLOWED_EXTENSIONS']),
                'max_records': current_app.config['MAX_RECORDS_PER_FILE'],
                'processing_timeout': current_app.config['PROCESSING_TIMEOUT']
            }
        })
    else:
        return jsonify({'error': 'Not available in production'}), 403


@api_bp.route('/system/metrics')
def api_system_metrics():
    """API for getting system metrics"""
    if not current_app.config['DEBUG']:
        return jsonify({'error': 'Not available in production'}), 403
    
    metrics = LogManager.get_system_metrics()
    return jsonify(metrics)

