import os
import json
import uuid
import logging
import random

from datetime import datetime
from werkzeug.utils import secure_filename
from flask import Blueprint, request, jsonify, current_app

from handlers.errors import ValidationError, ProcessingError


api_bp = Blueprint('api', __name__)

logger = logging.getLogger(__name__)


def allowed_file(filename):
    """Проверка разрешенных расширений файлов"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


def validate_json_schema(data):
    """Валидация структуры JSON"""
    required_fields = ['version', 'timestamp', 'data']
    
    for field in required_fields:
        if field not in data:
            raise ValidationError(f'Отсутствует обязательное поле: {field}')
    
    if not isinstance(data['data'], list):
        raise ValidationError('Поле "data" должно быть массивом')
    
    if not data['data']:
        raise ValidationError('Массив "data" не должен быть пустым')
    
    # Проверка лимита записей
    if len(data['data']) > current_app.config['MAX_RECORDS_PER_FILE']:
        raise ValidationError(
            f'Превышено максимальное количество записей: {current_app.config["MAX_RECORDS_PER_FILE"]}'
        )
    
    try:
        datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
    except (ValueError, TypeError):
        raise ValidationError('Неверный формат timestamp')
    
    return True


@api_bp.route('/upload', methods=['POST'])
def api_upload():
    """API для загрузки JSON файла"""
    if 'file' not in request.files:
        raise ValidationError('Файл не найден')
    
    file = request.files['file']
    
    if file.filename == '':
        raise ValidationError('Файл не выбран')
    
    if not (file and allowed_file(file.filename)):
        raise ValidationError('Неподдерживаемый формат файла')
    
    try:
        # Чтение и парсинг JSON
        file_content = file.read().decode('utf-8')
        json_data = json.loads(file_content)
        
        # Валидация
        validate_json_schema(json_data)
        
        # Сохранение файла
        filename = secure_filename(file.filename)
        file_id = str(uuid.uuid4())
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], f"{file_id}_{filename}")
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
        
        # Создание задачи обработки
        task_id = str(uuid.uuid4())
        
        logger.info(f"Файл загружен: {filename}, task_id: {task_id}, records: {len(json_data['data'])}")
        
        return jsonify({
            'success': True,
            'message': 'Файл успешно загружен и проверен',
            'task_id': task_id,
            'filename': filename,
            'file_size': len(file_content),
            'records_count': len(json_data['data'])
        })
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {str(e)}")
        raise ValidationError(f'Ошибка парсинга JSON: {str(e)}')
    except ValidationError:
        # Перебрасываем ValidationError без изменений
        raise
    except Exception as e:
        logger.error(f"Ошибка при обработке файла: {str(e)}")
        raise ProcessingError('Внутренняя ошибка сервера при обработке файла')


@api_bp.route('/start_processing', methods=['POST'])
def api_start_processing():
    """API для запуска обработки данных"""
    data = request.get_json()
    task_id = data.get('task_id')
    
    if not task_id:
        raise ValidationError('ID задачи не указан')
    
    # Здесь будет логика запуска обработки
    logger.info(f"Запущена обработка для task_id: {task_id}")
    
    return jsonify({
        'success': True,
        'message': 'Обработка данных запущена',
        'task_id': task_id,
        'status_url': '/status',
        'timeout': current_app.config['PROCESSING_TIMEOUT']
    })


@api_bp.route('/processing_status/<task_id>')
def api_processing_status(task_id):
    """API для получения статуса обработки"""
    # Имитация прогресса обработки
    progress = random.randint(10, 95)
    
    phases = [
        {'id': 'phase1', 'name': 'Загрузка файла', 'status': 'completed', 'progress': 100},
        {'id': 'phase2', 'name': 'Анализ данных', 'status': 'active', 'progress': progress},
        {'id': 'phase3', 'name': 'Обработка', 'status': 'pending', 'progress': 0},
        {'id': 'phase4', 'name': 'Формирование отчета', 'status': 'pending', 'progress': 0}
    ]
    
    return jsonify({
        'task_id': task_id,
        'status': 'processing',
        'overall_progress': progress,
        'current_phase': 'Анализ данных',
        'phases': phases,
        'logs': [
            {'timestamp': '10:23:15', 'level': 'info', 'message': 'Загрузка JSON-файла началась'},
            {'timestamp': '10:23:16', 'level': 'success', 'message': 'Файл успешно загружен и проверен'},
            {'timestamp': '10:23:17', 'level': 'info', 'message': 'Начало анализа входных данных...'},
            {'timestamp': '10:23:45', 'level': 'info', 'message': f'Обработано {progress}% данных...'}
        ]
    })


@api_bp.route('/results')
def api_results():
    """API для получения списка результатов"""
    # Имитация данных результатов
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
    """API для получения логов"""
    # Имитация логов
    levels = ['info', 'warning', 'error', 'debug']
    messages = [
        'Проверка целостности данных',
        'Оптимизация использования памяти',
        'Кэширование промежуточных результатов',
        'Экспорт данных во внешнюю систему',
        'Очистка временных файлов'
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
            'details': f'Детали для {message.lower()}'
        })
    
    return jsonify({'logs': logs})


@api_bp.route('/config')
def api_config():
    """API для получения информации о конфигурации (только для разработки)"""
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

