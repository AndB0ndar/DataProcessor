import os
from datetime import timedelta


basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Базовая конфигурация"""
    APP_NAME = "DataProcessor"

    # Безопасность
    SECRET_KEY = os.environ.get('SECRET_KEY') or '2ecc2d15309dba81fda24721ea014328c3a1de16d8a4964663549c906e825893'
    
    # Папки для файлов
    UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
    RESULTS_FOLDER = os.path.join(basedir, 'results')
    
    # Ограничения файлов
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS = {'json'}
    
    # Сессия
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # Логирование
    LOG_LEVEL = 'INFO'
    LOG_FORMAT = '%(asctime)s | %(name)s | [%(levelname)s] %(message)s'
    
    # Настройки обработки данных
    PROCESSING_TIMEOUT = 300  # 5 minutes
    MAX_RECORDS_PER_FILE = 100000
    
    # API настройки
    API_RATE_LIMIT = "100 per hour"
    
    @staticmethod
    def init_app(app):
        """Инициализация приложения с конфигурацией"""
        # Создание необходимых директорий
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        os.makedirs(app.config['RESULTS_FOLDER'], exist_ok=True)
        
        # Настройка логирования
        import logging
        logging.basicConfig(
            level=getattr(logging, app.config['LOG_LEVEL']),
            format=app.config['LOG_FORMAT']
        )


class DevelopmentConfig(Config):
    """Конфигурация для разработки"""
    DEBUG = True
    TESTING = False
    
    # Дополнительные настройки для разработки
    EXPLAIN_TEMPLATE_LOADING = False
    
    # Более детальное логирование
    LOG_LEVEL = 'DEBUG'


class TestingConfig(Config):
    """Конфигурация для тестирования"""
    TESTING = True
    DEBUG = False
    
    # Используем временные папки для тестов
    UPLOAD_FOLDER = os.path.join(basedir, 'test_uploads')
    RESULTS_FOLDER = os.path.join(basedir, 'test_results')
    
    # Отключаем CSRF для тестирования
    WTF_CSRF_ENABLED = False
    
    # Быстрая обработка для тестов
    PROCESSING_TIMEOUT = 30


class ProductionConfig(Config):
    """Конфигурация для продакшена"""
    DEBUG = False
    TESTING = False
    
    # Безопасность в продакшене - проверяем в init_app
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'fallback-secret-key-for-non-prod'
    
    # Более строгие ограничения в продакшене
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB
    MAX_RECORDS_PER_FILE = 50000
    
    # Логирование ошибок
    LOG_LEVEL = 'WARNING'
    
    @classmethod
    def init_app(cls, app):
        """Инициализация с проверкой для продакшена"""
        # Проверяем SECRET_KEY только если действительно в продакшене
        config_name = os.environ.get('FLASK_CONFIG', 'default')
        if config_name == 'production':
            secret_key = os.environ.get('SECRET_KEY')
            if not secret_key:
                raise ValueError(
                    "SECRET_KEY must be set in production environment! "
                    "Set FLASK_CONFIG=development for development or "
                    "set SECRET_KEY environment variable for production."
                )
        
        # Вызываем родительский init_app
        super(ProductionConfig, cls).init_app(app)


class DockerConfig(ProductionConfig):
    """Конфигурация для Docker окружения"""
    # Можно переопределить настройки для Docker
    pass


# Словарь для легкого доступа к конфигурациям
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'docker': DockerConfig,
    'default': DevelopmentConfig
}


def get_config():
    """Получение конфигурации на основе переменной окружения"""
    config_name = os.environ.get('FLASK_CONFIG', 'default')
    
    # Для безопасности, если указана production без SECRET_KEY, используем development
    if config_name == 'production' and not os.environ.get('SECRET_KEY'):
        print("Warning: FLASK_CONFIG=production but no SECRET_KEY set. Using development config.")
        return config['development']
    
    return config[config_name]

