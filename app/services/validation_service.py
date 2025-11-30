import os

from typing import Dict, List, Tuple
from werkzeug.datastructures import FileStorage


class FileValidationService:
    """Упрощенный сервис валидации файлов"""
    
    ALLOWED_CONFIG_EXTENSIONS = {'.json', '.yaml', '.yml', '.conf'}
    ALLOWED_SOURCES_EXTENSIONS = {'.v', '.vh', '.sv'}
    
    MAX_CONFIG_SIZE = 10 * 1024 * 1024  # 10MB
    MAX_SOURCES_SIZE = 50 * 1024 * 1024  # 50MB
    
    @classmethod
    def validate_upload(cls, config_file: FileStorage, source_files: List[FileStorage]) -> Tuple[bool, Dict]:
        """
        Валидация загружаемых файлов
        """
        validation_result = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        # Валидация конфигурационного файла
        config_valid, config_errors = cls._validate_config_file(config_file)
        if not config_valid:
            validation_result['valid'] = False
            validation_result['errors'].extend(config_errors)
        
        # Валидация исходных файлов
        sources_valid, sources_errors, sources_warnings = cls._validate_source_files(source_files)
        if not sources_valid:
            validation_result['valid'] = False
            validation_result['errors'].extend(sources_errors)
        
        validation_result['warnings'].extend(sources_warnings)
        
        return validation_result['valid'], validation_result
    
    @classmethod
    def _validate_config_file(cls, config_file: FileStorage) -> Tuple[bool, List[str]]:
        """Валидация конфигурационного файла"""
        errors = []
        
        # Проверка расширения
        file_ext = os.path.splitext(config_file.filename.lower())[1]
        if file_ext not in cls.ALLOWED_CONFIG_EXTENSIONS:
            errors.append(
                f'Неподдерживаемый формат конфигурационного файла: {file_ext}. '
                f'Допустимые форматы: {", ".join(cls.ALLOWED_CONFIG_EXTENSIONS)}'
            )
        
        # Проверка размера
        config_file.seek(0, os.SEEK_END)
        file_size = config_file.tell()
        config_file.seek(0)
        
        if file_size > cls.MAX_CONFIG_SIZE:
            errors.append(
                f'Конфигурационный файл слишком большой: {cls._format_size(file_size)}. '
                f'Максимальный размер: {cls._format_size(cls.MAX_CONFIG_SIZE)}'
            )
        
        return len(errors) == 0, errors
    
    @classmethod
    def _validate_source_files(cls, source_files: List[FileStorage]) -> Tuple[bool, List[str], List[str]]:
        """Валидация исходных файлов Verilog"""
        errors = []
        warnings = []
        
        if not source_files:
            errors.append('Не предоставлены исходные файлы Verilog')
            return False, errors, warnings
        
        if len(source_files) > 10:
            warnings.append('Загружено много исходных файлов. Рекомендуется не более 10.')
        
        valid_files_count = 0
        
        for source_file in source_files:
            file_valid, file_errors, file_warnings = cls._validate_single_source_file(source_file)
            
            if file_valid:
                valid_files_count += 1
            else:
                errors.extend(file_errors)
            
            warnings.extend(file_warnings)
        
        if valid_files_count == 0:
            errors.append('Нет валидных исходных файлов Verilog')
        
        return len(errors) == 0, errors, warnings
    
    @classmethod
    def _validate_single_source_file(cls, source_file: FileStorage) -> Tuple[bool, List[str], List[str]]:
        """Валидация одного исходного файла"""
        errors = []
        warnings = []
        
        # Проверка расширения
        file_ext = os.path.splitext(source_file.filename.lower())[1]
        if file_ext not in cls.ALLOWED_SOURCES_EXTENSIONS:
            errors.append(
                f'Файл {source_file.filename}: неподдерживаемый формат. '
                f'Допустимые форматы: {", ".join(cls.ALLOWED_SOURCES_EXTENSIONS)}'
            )
            return False, errors, warnings
        
        # Проверка размера
        source_file.seek(0, os.SEEK_END)
        file_size = source_file.tell()
        source_file.seek(0)
        
        if file_size > cls.MAX_SOURCES_SIZE:
            errors.append(
                f'Файл {source_file.filename} слишком большой: {cls._format_size(file_size)}. '
                f'Максимальный размер: {cls._format_size(cls.MAX_SOURCES_SIZE)}'
            )
            return False, errors, warnings
        
        # Базовая проверка на текстовый файл
        try:
            content = source_file.read(1024).decode('utf-8')
            source_file.seek(0)
        except UnicodeDecodeError:
            warnings.append(f'Файл {source_file.filename} может содержать бинарные данные')
        
        return len(errors) == 0, errors, warnings
    
    @classmethod
    def _format_size(cls, size_bytes: int) -> str:
        """Форматирование размера файла"""
        if size_bytes == 0:
            return "0B"
        
        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f}{size_names[i]}"

