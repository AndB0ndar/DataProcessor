import logging

from flask import jsonify, render_template, request


logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Custom exception for validation errors"""
    def __init__(self, message, status_code=400):
        super().__init__()
        self.message =message
        self.status_code = status_code


class ProcessingError(Exception):
    """Custom exception for processing errors"""
    def __init__(self, message, status_code=500):
        super().__init__()
        self.message =message
        self.status_code = status_code


def register_error_handlers(app):
    """Registration of all error handlers in the app"""
    
    @app.errorhandler(400)
    def bad_request_error(error):
        """Error 400 - Invalid request"""
        logger.warning(f'bad request: {error}')
        
        if request.is_json:
            return jsonify({
                'error': 'Bad request',
                'message': 'The request was malformed or contains invalid parameters',
                'code': 400
            }), 400
        
        return render_template('errors/400.html'), 400

    @app.errorhandler(403)
    def forbidden_error(error):
        """Error 403 - Access denied"""
        logger.warning(f' Forbidden access: {error}')
        
        if request.is_json:
            return jsonify({
                'error': 'Forbidden',
                'message': 'You do not have permission to access this resource',
                'code': 403
            }), 403
        
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def not_found_error(error):
        """Error 404 - Resource not found"""
        logger.error(f'resource not found: {request.url}')
            
        if request.is_json:
            return jsonify({
                'error': 'Resource not found',
                'message': 'The requested resource was not found on this server',
                'code': 404
            }), 404
        
        return render_template('errors/404.html'), 404

    @app.errorhandler(413)
    def too_large_error(error):
        """Error 413 - File too large"""
        logger.warning(f'file too large: {error}')
        
        max_size_mb = app.config['MAX_CONTENT_LENGTH'] // (1024 * 1024)
        
        if request.is_json:
            return jsonify({
                'error': 'File too large',
                'message': f'File size exceeds the limit of {max_size_mb}MB',
                'max_size_mb': max_size_mb,
                'code': 413
            }), 413
        
        return render_template('errors/413.html', max_size_mb=max_size_mb), 413

    @app.errorhandler(429)
    def too_many_requests_error(error):
        """Error 429 - Too many requests"""
        logger.warning(f' Too many requests from {request.remote_addr}')
        
        if request.is_json:
            return jsonify({
                'error': 'Too many requests',
                'message': 'Rate limit exceeded. Please try again later.',
                'code': 429
            }), 429
        
        return render_template('errors/429.html'), 429

    @app.errorhandler(500)
    def internal_error(error):
        """Error 500 - Internal server error"""
        logger.error(f'internal server error: {error}')
        
        if request.is_json:
            return jsonify({
                'error': 'Internal server error',
                'message': 'An internal server error occurred',
                'code': 500
            }), 500
        
        return render_template('errors/500.html'), 500

    @app.errorhandler(503)
    def service_unavailable_error(error):
        """Error 503 - Service unavailable"""
        logger.error(f'SERVICE unavailable: {error}')
        
        if request.is_json:
            return jsonify({
                'error': 'Service unavailable',
                'message': 'The service is temporarily unavailable. Please try again later.',
                'code': 503
            }), 503
        
        return render_template('errors/503.html'), 503

    @app.errorhandler(ValidationError)
    def validation_error(error):
        """Handling custom validation errors"""
        logger.warning(f'validation error: {error.message}')
        
        if request.is_json:
            return jsonify({
                'error': 'Validation error',
                'message': error.message,
                'code': error.status_code
            }), error.status_code
        
        return render_template('errors/validation.html', message=error.message), error.status_code

    @app.errorhandler(ProcessingError)
    def processing_error(error):
        """Handling custom processing errors"""
        logger.error(f'processing error: {error.message}')
            
        if request.is_json:
            return jsonify({
                'error': 'Processing error',
                'message': error.message,
                'code': error.status_code
            }), error.status_code
        
        return render_template('errors/processing.html', message=error.message), error.status_code

    # Handling common exceptions
    @app.errorhandler(Exception)
    def handle_generic_error(error):
        """Handling all unexpected exceptions"""
        logger.error(f'unhandled exception: {error}', exc_info=True)
        
        if request.is_json:
            return jsonify({
                'error': 'Internal server error',
                'message': 'An unexpected error occurred',
                'code': 500
            }), 500
        
        return render_template('errors/generic.html'), 500
