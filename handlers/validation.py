import os
import json

from flask import request, current_app
from datetime import datetime

from .errors import ValidationError


class JSONValidator:
    """Validator of JSON files and data"""
    
    @staticmethod
    def validate_file_upload(file):
        """Validation of the uploaded file"""
        if not file:
            raise ValidationError('File not provided')
        
        if file.filename == '':
            raise ValidationError('The file name cannot be empty')
        
        if not JSONValidator.allowed_file(file.filename):
            raise ValidationError('Unsupported file format')
        
        # Checking the file size
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > current_app.config['MAX_CONTENT_LENGTH']:
            max_size_mb = current_app.config['MAX_CONTENT_LENGTH'] // (1024 * 1024)
            raise ValidationError(f' File size exceeds {max_size_mb}MB')
        
        return True
    
    @staticmethod
    def allowed_file(filename):
        """Checking the file extension"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']
    
    @staticmethod
    def validate_json_structure(data):
        """Validation of the JSON structure"""
        required_fields = ['version', 'timestamp', 'data']
        
        for field in required_fields:
            if field not in data:
                raise ValidationError(f'Required field is missing: {field}')
        
        if not isinstance(data['data'], list):
            raise ValidationError('The "data" field must be an array')
        
        if not data['data']:
            raise ValidationError('The "data" array must not be empty')
        
        # Checking the record limit
        if len(data['data']) > current_app.config['MAX_RECORDS_PER_FILE']:
            raise ValidationError(
                f' The maximum number of records has been exceeded: {current_app.config["MAX_RECORDS_PER_FILE"]}'
            )
        
        # Timestamp validation
        try:
            datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
        except (ValueError, TypeError):
            raise ValidationError('Invalid timestamp format')
        
        # Version validation
        if not isinstance(data['version'], str):
            raise ValidationError('The "version" field must be a string')
        
        return True
    
    @staticmethod
    def validate_json_content(data):
        """Data content validation"""
        for i, item in enumerate(data['data']):
            if not isinstance(item, dict):
                raise ValidationError(f' Data element {i} must be an object')
            
            # Checking required fields in each element
            if 'id' not in item:
                raise ValidationError(f' Data element {i} does not contain the "id" field')
        
        return True


class QueryParamValidator:
    """Query parameter validator"""
    
    @staticmethod
    def validate_pagination_params(page, per_page):
        """Validation of pagination parameters"""
        try:
            page = int(page) if page else 1
            per_page = int(per_page) if per_page else 20
        except ValueError:
            raise ValidationError('Pagination parameters must be numbers')
        
        if page < 1:
            raise ValidationError('The page number must be a positive number')
        
        if per_page < 1 or per_page > 100:
            raise ValidationError('The number of items on the page must be from 1 to 100')
        
        return page, per_page
    
    @staticmethod
    def validate_sort_params(sort_by, sort_order):
        """Validation of sorting parameters"""
        allowed_sort_fields = ['name', 'date', 'status', 'size']
        allowed_orders = ['asc', 'desc']
        
        if sort_by and sort_by not in allowed_sort_fields:
            raise ValidationError(f' Invalid sorting field: {sort_by}')
        
        if sort_order and sort_order not in allowed_orders:
            raise ValidationError(f' Invalid sorting direction: {sort_order}')
        
        return sort_by or 'date', sort_order or 'desc'
