import os
import json
import logging
import zipfile

from datetime import datetime
from werkzeug.utils import secure_filename

from flask import current_app

from app import db
from app.models.run import Run, RunStatus, RunStage


logger = logging.getLogger(__name__)


class RunService:
    @staticmethod
    def get_runs_folder():
        return current_app.config.get('RUNS_FOLDER', 'runs')

    @staticmethod
    def get_project_folder(run_id):
        return os.path.join(RunService.get_runs_folder(), f'run_{run_id}')
    
    @staticmethod
    def create_run(session_id, email):
        run = Run(session_id=session_id, email=email)
        db.session.add(run)
        db.session.commit()
        return run
    
    @staticmethod
    def save_uploaded_files(run_id, config_file, source_files):
        run = Run.query.get(run_id)
        if not run:
            return False
        
        project_dir = RunService.get_project_folder(run_id)
        os.makedirs(project_dir, exist_ok=True)

        try:
            config_filename = secure_filename(config_file.filename)
            config_path = os.path.join(project_dir, config_filename)
            config_file.save(config_path)
            
            source_filenames = []
            for source_file in source_files:
                source_filename = secure_filename(source_file.filename)
                source_path = os.path.join(project_dir, source_filename)
                source_file.save(source_path)
                source_filenames.append(source_filename)

            # FIXME: save path to rtl dir
            run.config_filename = config_filename
            run.sources_filenames = json.dumps(source_filenames)
            db.session.commit()
            
            logger.info(f"Saved files for run {run_id}: config={config_filename}, sources={source_filenames}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving files for run {run_id}: {str(e)}")
            return False
    
    @staticmethod
    def update_run_stage(run_id, current_stage, completed_stages=None, progress=0):
        run = Run.query.get(run_id)
        if not run:
            return None

        if current_stage:
            run.current_stage = RunStage(current_stage)
        
        if completed_stages is not None:
            run.completed_stages_list = completed_stages
        
        run.progress = progress

        try:
            db.session.commit()
            return run
        except Exception as e:
            db.session.rollback()
            return None
    
    @staticmethod
    def update_run_logs(run_id, log_content=None):
        run = Run.query.get(run_id)
        if not run:
            return None
        
        if log_content is not None:
            # FIXME
            timestamp = datetime.utcnow().strftime('%H:%M:%S')
            formatted_output = f"[{timestamp}] {log_content}"
            
            if run.log_content:
                run.log_content += formatted_output
            else:
                run.log_content = formatted_output

        db.session.commit()
        return run
    
    @staticmethod
    def set_run_status(run_id, status, start_time=None, end_time=None):
        run = Run.query.get(run_id)
        if not run:
            return None
        
        run.status = RunStatus(status)
        
        if start_time:
            run.start_time = start_time
        if end_time:
            run.end_time = end_time
        
        db.session.commit()
        return run

    @staticmethod
    def complete(run_id):
        run = Run.query.get(run_id)
        if not run:
            return None
        run.f_completed = True
    
    @staticmethod
    def create_results_archive(run_id):
        run = Run.query.get(run_id)
        if not run:
            return None
        
        run_dir = RunService.get_project_folder(run_id)
        if not os.path.exists(run_dir):
            return None
        
        archive_path = os.path.join(run_dir, f'results_{run_id}.zip')
        
        with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(run_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, run_dir)
                    zipf.write(file_path, arcname)
        
        run.archive_filename = f'results_{run_id}.zip'
        db.session.commit()
        
        return archive_path
    
    @staticmethod
    def has_active_run(session_id):
        """Проверяет, есть ли у пользователя активный запуск"""
        active_statuses = [RunStatus.PENDING, RunStatus.RUNNING]
        active_run = Run.query.filter(
            Run.session_id == session_id,
            Run.status.in_(active_statuses)
        ).first()
        return active_run is not None

    @staticmethod
    def get_last_run(session_id):
        """Получает последний запуск для сессии"""
        return Run.query.filter_by(
            session_id=session_id
        ).order_by(Run.created_at.desc()).first()
    
    @staticmethod
    def get_active_run(session_id):
        """Возвращает активный запуск пользователя"""
        active_statuses = [RunStatus.PENDING, RunStatus.RUNNING]
        return Run.query.filter(
            Run.session_id == session_id,
            Run.status.in_(active_statuses)
        ).first()

    @staticmethod
    def get_user_runs(session_id, limit=None):
        """Возвращает все запуски пользователя"""
        query = Run.query.filter_by(session_id=session_id).order_by(Run.created_at.desc())
        if limit:
            query = query.limit(limit)
        return query.all()

