import enum
import json

from datetime import datetime

from app import db


class RunStatus(enum.Enum):
    PENDING = 'pending'
    RUNNING = 'running'
    COMPLETED = 'completed'
    FAILED = 'failed'
    CANCELLED = 'cancelled'


class RunStage(enum.Enum):
    NONE = '-'
    SYNTHESIS = 'synthesis'
    PLACEMENT = 'placement'
    ROUTING = 'routing'
    TIMING = 'timing'
    POWER = 'power'
    FINISHED = 'finished'


class Run(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False, index=True)
    session_id = db.Column(db.Integer, db.ForeignKey('session.id'))
    
    # Информация о файлах
    config_filename = db.Column(db.String(200))
    sources_filenames = db.Column(db.Text, default='[]')
    archive_filename = db.Column(db.String(200))
    
    # Статус выполнения
    status = db.Column(db.Enum(RunStatus), default=RunStatus.PENDING)
    current_stage = db.Column(db.Enum(RunStage), default=RunStage.NONE)
    completed_stages = db.Column(db.Text, default='[]')  # JSON список выполненных стадий
    progress = db.Column(db.Integer, default=0)  # 0-100%
    
    # Временные метки
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Логи
    log_content = db.Column(db.Text)
    
    # Связи
    session = db.relationship('Session', backref=db.backref('runs', lazy=True))
    
    @property
    def completed_stages_list(self):
        return json.loads(self.completed_stages)
    
    @completed_stages_list.setter
    def completed_stages_list(self, value):
        self.completed_stages = json.dumps(value)
    
    @property
    def duration(self):
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        elif self.start_time:
            return datetime.utcnow() - self.start_time
        return None
    
    @property
    def pending_stages(self):
        all_stages = [stage for stage in RunStage]
        completed = self.completed_stages_list
        current = self.current_stage.value
        
        pending = []
        for stage in all_stages:
            if stage.value not in completed and stage.value != current:
                pending.append(stage.value)
        return pending
    
    @property
    def f_completed(self):
        """Для обратной совместимости с шаблоном"""
        return self.status == RunStatus.COMPLETED
    
    @property
    def is_running(self):
        """Запуск выполняется"""
        return self.status == RunStatus.RUNNING
    
    @property
    def is_finished(self):
        """Запуск завершен (успешно или с ошибкой)"""
        return self.status in [RunStatus.COMPLETED, RunStatus.FAILED, RunStatus.CANCELLED]
    
    def to_dict(self):
        return {
            'id': self.id,
            'status': self.status.value,
            'current_stage': self.current_stage.value,
            'completed_stages': self.completed_stages_list,
            'pending_stages': self.pending_stages,
            'progress': self.progress,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration': str(self.duration) if self.duration else None,
            'log_content': self.log_content,
            'is_finished': self.is_finished,
            'is_running': self.is_running
        }

