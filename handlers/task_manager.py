import uuid
import time
import logging
import threading

from flask import current_app
from datetime import datetime, timedelta

from .errors import ProcessingError


logger = logging.getLogger(__name__)


class TaskStatus:
    PENDING = 'pending'
    PROCESSING = 'processing'
    COMPLETED = 'completed'
    FAILED = 'failed'
    CANCELLED = 'cancelled'


class TaskManager:
    """Processing Task Manager"""
    
    _tasks = {}
    _lock = threading.Lock()
    
    @classmethod
    def create_task(cls, file_path, user_id=None):
        """Creating a new task"""
        task_id = str(uuid.uuid4())
        
        with cls._lock:
            cls._tasks[task_id] = {
                'id': task_id,
                'file_path': file_path,
                'user_id': user_id,
                'status': TaskStatus.PENDING,
                'progress': 0,
                'current_phase': 'Initialization',
                'phases': [],
                'created_at': datetime.now(),
                'started_at': None,
                'completed_at': None,
                'error_message': None,
                'result_data': None
            }
        
        logger.info(f"Task created: {task_id}")
        return task_id
    
    @classmethod
    def start_processing(cls, task_id):
        """Starting task processing"""
        with cls._lock:
            if task_id not in cls._tasks:
                raise ProcessingError('Task not found')
            
            task = cls._tasks[task_id]
            task['status'] = TaskStatus.PROCESSING
            task['started_at'] = datetime.now()
            
            # Simulation of processing phases
            task['phases'] = [
                {'id': 'phase1', 'name': 'File upload', 'status': TaskStatus.PENDING, 'progress': 0},
                {'id': 'phase2', 'name': 'Data analysis', 'status': TaskStatus.PENDING, 'progress': 0},
                {'id': 'phase3', 'name': 'Processing', 'status': TaskStatus.PENDING, 'progress': 0},
                {'id': 'phase4', 'name': 'Report generation', 'status': TaskStatus.PENDING, 'progress': 0}
            ]
        
        # Start processing in a separate thread
        thread = threading.Thread(target=cls._process_task, args=(task_id,))
        thread.daemon = True
        thread.start()
        
        logger.info(f"Task processing started: {task_id}")
    
    @classmethod
    def _process_task(cls, task_id):
        """Background task processing (simulation)"""
        try:
            # Phase 1: File Upload
            cls._update_phase(task_id, 'phase1', TaskStatus.PROCESSING)
            time.sleep(2)
            cls._update_phase(task_id, 'phase1', TaskStatus.COMPLETED, 100)
            cls._update_task_progress(task_id, 25)
            
            # Phase 2: Data Analysis
            cls._update_phase(task_id, 'phase2', TaskStatus.PROCESSING)
            for i in range(10):
                time.sleep(1)
                progress = (i + 1) * 10
                cls._update_phase(task_id, 'phase2', TaskStatus.PROCESSING, progress)
                cls._update_task_progress(task_id, 25 + (progress * 0.4))
            cls._update_phase(task_id, 'phase2', TaskStatus.COMPLETED, 100)
            
            # Phase 3: Processing
            cls._update_phase(task_id, 'phase3', TaskStatus.PROCESSING)
            for i in range(5):
                time.sleep(1.5)
                progress = (i + 1) * 20
                cls._update_phase(task_id, 'phase3', TaskStatus.PROCESSING, progress)
                cls._update_task_progress(task_id, 65 + (progress * 0.2))
            cls._update_phase(task_id, 'phase3', TaskStatus.COMPLETED, 100)
            
            # Phase 4: Report Generation
            cls._update_phase(task_id, 'phase4', TaskStatus.PROCESSING)
            time.sleep(3)
            cls._update_phase(task_id, 'phase4', TaskStatus.COMPLETED, 100)
            
            # Task Completion
            cls._complete_task(task_id)
            
        except Exception as e:
            logger.error(f"Error processing task {task_id}: {str(e)}")
            cls._fail_task(task_id, str(e))
    
    @classmethod
    def _update_phase(cls, task_id, phase_id, status, progress=0):
        """Phase status update"""
        with cls._lock:
            if task_id not in cls._tasks:
                return
            for phase in cls._tasks[task_id]['phases']:
                if phase['id'] == phase_id:
                    phase['status'] = status
                    phase['progress'] = progress
                    if status == TaskStatus.PROCESSING:
                        cls._tasks[task_id]['current_phase'] = phase['name']
                    break
    
    @classmethod
    def _update_task_progress(cls, task_id, progress):
        """Updating the overall progress of the task"""
        with cls._lock:
            if task_id in cls._tasks:
                cls._tasks[task_id]['progress'] = min(100, progress)
    
    @classmethod
    def _complete_task(cls, task_id):
        """Completing the task with success"""
        with cls._lock:
            if task_id in cls._tasks:
                cls._tasks[task_id].update({
                    'status': TaskStatus.COMPLETED,
                    'progress': 100,
                    'completed_at': datetime.now(),
                    'result_data': {
                    'message': 'Processing completed successfully',
                        'records_processed': 1000,
                        'processing_time': '00:02:30'
                    }
                })
        logger.info(f"Task completed: {task_id}")
    
    @classmethod
    def _fail_task(cls, task_id, error_message):
        """Task completion with error"""
        with cls._lock:
            if task_id in cls._tasks:
                cls._tasks[task_id].update({
                    'status': TaskStatus.FAILED,
                    'error_message': error_message,
                    'completed_at': datetime.now()
            })
        logger.error(f"Task completed with error: {task_id}")
    
    @classmethod
    def get_task_status(cls, task_id):
        """Getting the issue status"""
        with cls._lock:
            return cls._tasks.get(task_id)
    
    @classmethod
    def cancel_task(cls, task_id):
        """Canceling a task"""
        with cls._lock:
            if task_id in cls._tasks and cls._tasks[task_id]['status'] == TaskStatus.PROCESSING:
                cls._tasks[task_id].update({
                    'status': TaskStatus.CANCELLED,
                    'completed_at': datetime.now()
                })
                return True
        return False
    
    @classmethod
    def cleanup_old_tasks(cls, hours=24):
        """Cleaning up old tasks"""
        cutoff = datetime.now() - timedelta(hours=hours)
        
        count_removed = 0
        with cls._lock:
            tasks_to_remove = [
                task_id for task_id, task in cls._tasks.items()
                if task['created_at'] < cutoff and task['status'] in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]
            ]
            
            for task_id in tasks_to_remove:
                del cls._tasks[task_id]

            count_removed = len(tasks_to_remove)
        
        logger.info(f"Cleared {count_removed} old tasks")
        return count_removed

