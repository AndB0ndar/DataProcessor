import os
import time
import queue
import threading
import subprocess

from datetime import datetime

from flask import current_app

from app.models.run import RunStatus, RunStage
from app.services.run_service import RunService


class LibreLaneService:
    _run_queue = queue.Queue()
    _active_runs = {}
    _worker_thread = None
    _app = None

    @classmethod
    def init_service(cls, app):
        cls._app = app
        cls._start_worker()

    @classmethod
    def _start_worker(cls):
        if cls._worker_thread and cls._worker_thread.is_alive():
            return
        
        cls._worker_thread = threading.Thread(target=cls._worker_loop, daemon=True)
        cls._worker_thread.start()

    @classmethod
    def _worker_loop(cls):
        while True:
            run_id = cls._run_queue.get()
            if run_id is None:
                break
            
            with cls._app.app_context():
                cls._execute_librelane(run_id)
            
            cls._run_queue.task_done()

    @classmethod
    def _execute_librelane(cls, run_id):
        from app import db
        from app.models.run import Run
        
        run = Run.query.get(run_id)
        if not run:
            return
        
        try:
            # Обновляем статус
            RunService.set_run_status(run_id, 'running', start_time=datetime.utcnow())
            
            # Имитация выполнения стадий LibreLane с реальными обновлениями
            stages = [
                (RunStage.SYNTHESIS, 20, "Synthesis started..."),
                (RunStage.PLACEMENT, 40, "Placement in progress..."),
                (RunStage.ROUTING, 60, "Routing components..."),
                (RunStage.TIMING, 80, "Timing analysis..."),
                (RunStage.POWER, 95, "Power optimization..."),
                (RunStage.FINISHED, 100, "Finalizing...")
            ]
            
            completed_stages = []
            for stage, target_progress, stage_message in stages:
                # Проверяем не отменен ли запуск
                if not cls._active_runs.get(run_id):
                    break
                
                # Обновляем текущую стадию
                RunService.update_run_stage(
                    run_id, 
                    stage.value, 
                    completed_stages, 
                    target_progress - 10
                )
                
                # Добавляем сообщение о начале стадии
                RunService.update_run_logs(run_id, log_content=f"\n=== {stage.value.upper()} ===\n")
                RunService.update_run_logs(run_id, log_content=f"{stage_message}\n")
                
                # Имитация прогресса внутри стадии
                for step in range(5):
                    if not cls._active_runs.get(run_id):
                        break
                    
                    time.sleep(0.5)  # Имитация работы
                    
                    # Постепенно увеличиваем прогресс
                    current_progress = target_progress - 10 + (step * 2)
                    RunService.update_run_stage(
                        run_id, 
                        stage.value, 
                        completed_stages, 
                        current_progress
                    )
                    
                    # Добавляем прогресс в логи
                    RunService.update_run_logs(run_id, log_content=f"Progress: {current_progress}%\n")
                
                # Завершаем стадию
                completed_stages.append(stage.value)
                RunService.update_run_stage(
                    run_id, 
                    stage.value, 
                    completed_stages, 
                    target_progress
                )
                
                RunService.update_run_logs(run_id, log_content=f"Stage {stage.value} completed\n")
            
            # Завершаем запуск
            if cls._active_runs.get(run_id):
                RunService.set_run_status(run_id, 'completed', end_time=datetime.utcnow())
                # Создаем архив с результатами
                archive_path = RunService.create_results_archive(run_id)
                if archive_path:
                    RunService.update_run_logs(run_id, log_content=f"\nResults archived: {archive_path}\n")
                RunService.update_run_logs(run_id, log_content="\n=== RUN COMPLETED SUCCESSFULLY ===\n")
            else:
                RunService.set_run_status(run_id, 'cancelled', end_time=datetime.utcnow())
                RunService.update_run_logs(run_id, log_content="\n=== RUN CANCELLED ===\n")

        except Exception as e:
            RunService.set_run_status(run_id, 'failed', end_time=datetime.utcnow())
            RunService.update_run_logs(run_id, log_content=str(e))
        finally:
            cls._active_runs.pop(run_id, None)

    @classmethod
    def _librelane(cls, run_id):
        from app import db
        from app.models.run import Run
        
        run = Run.query.get(run_id)
        if not run:
            return
        
        try:
            project_dir = RunService.get_project_folder(run_id)
            config_path = os.path.join(project_dir, run.config_filename)
            
            # Обновляем статус
            RunService.set_run_status(run_id, 'running', start_time=datetime.utcnow())
            
            # Формируем команду LibreLane из конфига
            librelane_cmd = current_app.config.get('LIBRELANE_COMMAND', 'librelane')
            librelane_base_dir = current_app.config.get('LIBRELANE_BASE_DIR', '')
            
            cmd = [
                librelane_cmd,
                '--config', config_path,
                '--run-dir', project_dir,
                '--log', os.path.join(project_dir, 'output.log')
            ]
            
            # Запускаем реальную команду LibreLane
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=librelane_base_dir or None
            )
            
            cls._active_runs[run_id] = process
            
            # Читаем вывод в реальном времени
            output_lines = []
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    output_lines.append(output)
                    # Обновляем логи в реальном времени
                    RunService.update_run_logs(run_id, log_content=''.join(output_lines))
            
            stdout, stderr = process.communicate()
            
            # Финальное обновление статуса
            if process.returncode == 0:
                RunService.set_run_status(run_id, 'completed', end_time=datetime.utcnow())
                RunService.complete(run_id)
                RunService.create_results_archive(run_id)
            else:
                RunService.set_run_status(run_id, 'failed', end_time=datetime.utcnow())
                RunService.update_run_logs(run_id, log_content=stderr)
                
        except Exception as e:
            RunService.set_run_status(run_id, 'failed', end_time=datetime.utcnow())
            RunService.update_run_logs(run_id, log_content=str(e))
        finally:
            cls._active_runs.pop(run_id, None)

    @classmethod
    def submit_run(cls, run_id):
        cls._active_runs[run_id] = True
        cls._run_queue.put(run_id)

    @classmethod
    def cancel_run(cls, run_id):
        if run_id in cls._active_runs:
            cls._active_runs[run_id] = False
            return True
        return False
