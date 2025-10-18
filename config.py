import os
from datetime import timedelta


basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Basic configuration"""
    APP_NAME = "DataProcessor"

    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY') or '2ecc2d15309dba81fda24721ea014328c3a1de16d8a4964663549c906e825893'
    
    # File folders
    UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
    RESULTS_FOLDER = os.path.join(basedir, 'results')
    
    # File Restrictions
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS = {'json'}
    
    # Session
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # Logging
    LOG_LEVEL = 'INFO'
    LOG_FORMAT = '%(asctime)s | %(name)s | [%(levelname)s] %(message)s'
    
    # Data processing settings
    PROCESSING_TIMEOUT = 300  # 5 minutes
    MAX_RECORDS_PER_FILE = 100000
    
    # API settings
    API_RATE_LIMIT = "100 per hour"
    
    @staticmethod
    def init_app(app):
        """Initializing the application with the configuration"""
        # Creating the necessary directories
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        os.makedirs(app.config['RESULTS_FOLDER'], exist_ok=True)


class DevelopmentConfig(Config):
    """Configuration for development"""
    DEBUG = True
    TESTING = False
    
    # Additional settings for development
    EXPLAIN_TEMPLATE_LOADING = False
    
    # More detailed logging
    LOG_LEVEL = 'DEBUG'


class TestingConfig(Config):
    """Configuration for testing"""
    TESTING = True
    DEBUG = False
    
    # We use temporary folders for tests
    UPLOAD_FOLDER = os.path.join(basedir, 'test_uploads')
    RESULTS_FOLDER = os.path.join(basedir, 'test_results')
    
    # Disabling CSRF for testing
    WTF_CSRF_ENABLED = False
    
    # Fast processing for tests
    PROCESSING_TIMEOUT = 30


class ProductionConfig(Config):
    """Configuration for production"""
    DEBUG = False
    TESTING = False
    
    # Security in production - check in init_app
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'fallback-secret-key-for-non-prod'
    
    # Stricter restrictions in production
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB
    MAX_RECORDS_PER_FILE = 50000
    
    # Error logging
    LOG_LEVEL = 'WARNING'
    
    @classmethod
    def init_app(cls, app):
        """Initialization with verification for production"""
        # We check SECRET_KEY only if it is valid in production
        config_name = os.environ.get('FLASK_CONFIG', 'default')
        if config_name == 'production':
            secret_key = os.environ.get('SECRET_KEY')
            if not secret_key:
                raise ValueError(
                    "SECRET_KEY must be set in production environment! "
                    "Set FLASK_CONFIG=development for development or "
                    "set SECRET_KEY environment variable for production."
                )
        
        # Calling the parent init_app
        super(ProductionConfig, cls).init_app(app)


class DockerConfig(ProductionConfig):
    """Configuration for the Docker environment"""
    # You can redefine the settings for Docker
    pass


# Dictionary for easy access to configurations
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'docker': DockerConfig,
    'default': DevelopmentConfig
}


def get_config():
    """Getting configuration based on environment variable"""
    config_name = os.environ.get('FLASK_CONFIG', 'default')
    
    # For security, if production is specified without SECRET_KEY, we use development
    if config_name == 'production' and not os.environ.get('SECRET_KEY'):
        print("Warning: FLASK_CONFIG=production but no SECRET_KEY set. Using development config.")
        return config['development']
    
    return config[config_name]

