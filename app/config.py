import os
from datetime import timedelta


class Config:
    """Basic configuration"""
    APP_NAME = "DataProcessor"

    APPLICATION_ROOT = os.environ.get('APPLICATION_ROOT', '/')
    ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

    HOST = os.environ.get('HOST', "0.0.0.0")
    PORT = os.environ.get('PORT', 5000)

    DEBUG = True

    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'

    # DATABASE
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///librelane.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Session
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # File folders
    RUNS_FOLDER = os.path.abspath(os.environ.get('RUNS_FOLDER') or 'runs')
    LOG_FOLDER = os.path.abspath('logs')

    # File Restrictions
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS = {'json', 'v', 'tar', 'tar.gz'}
    
    # Logging
    LOG_LEVEL = 'INFO'
    LOG_FORMAT = '%(asctime)s | %(name)s | [%(levelname)s] %(message)s'
    
    # Data processing settings
    PROCESSING_TIMEOUT = 300  # 5 minutes
    MAX_RECORDS_PER_FILE = 100000
    
    # API settings
    API_RATE_LIMIT = "100 per hour"

    # Email (for send magic links)
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@librelane.example.com')
    
    @staticmethod
    def init_app(app):
        """Initializing the application with the configuration"""
        # Creating the necessary directories
        os.makedirs(app.config['RUNS_FOLDER'], exist_ok=True)


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
    RUNS_FOLDER = os.path.abspath('test_runs')
    
    # Disabling CSRF for testing
    WTF_CSRF_ENABLED = False
    
    # Fast processing for tests
    PROCESSING_TIMEOUT = 30

    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


class ProductionConfig(Config):
    """Configuration for production"""
    DEBUG = False
    TESTING = False
    
    # Stricter restrictions in production
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB
    MAX_RECORDS_PER_FILE = 50000
    
    # Error logging
    LOG_LEVEL = 'WARNING'
    
    @classmethod
    def init_app(cls, app):
        """Initialization with verification for production"""
        # Security in production
        # We check SECRET_KEY only if it is valid in production
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

