import os
import logging

from flask import Blueprint
from flask import flash, jsonify, redirect, send_file, request, session, url_for

from app.models.run import Run
from app.utils.decorators import (
    login_required, 
    no_active_run_required,
    run_ownership_required,
    run_completed_required,
    run_not_completed_required
)
from app.services.run_service import RunService
from app.services.librelane_service import LibreLaneService


api_bp = Blueprint('api', __name__)

logger = logging.getLogger(__name__)


@api_bp.route('/upload', methods=['POST'])
@login_required
@no_active_run_required
def upload():
    try:
        uploaded_files = request.files.getlist('files')
        if not uploaded_files or all(not file.filename for file in uploaded_files):
            return jsonify({'success': False, 'error': 'Нет загруженных файлов'}), 400
        
        config_files = []
        source_files = []

        for file in uploaded_files:
            if not file.filename:
                continue

            filename_lower = file.filename.lower()
            if any(filename_lower.endswith(ext) for ext in ['.json', '.yaml', '.yml', '.conf']):
                config_files.append(file)
            elif any(filename_lower.endswith(ext) for ext in ['.v', '.vh', '.sv']):
                source_files.append(file)
            else:
                return jsonify({
                    'success': False,
                    'error': f'Неподдерживаемый формат файла: {file.filename}'
                }), 400
        
        from app.services.validation_service import FileValidationService
        is_valid, validation_result = FileValidationService.validate_upload(
            config_files[0] if config_files else None,
            source_files
        )
        if not is_valid:
            return jsonify({
                'success': False,
                'error': 'Ошибки валидации файлов',
                'details': validation_result['errors']
            }), 400
        if validation_result['warnings']:
            logging.warning(f"File upload warnings: {validation_result['warnings']}")
        

        run = RunService.create_run(session['session_id'], session['email'])
        
        config_file = config_files[0]
        if RunService.save_uploaded_files(run.id, config_file, source_files):
            LibreLaneService.submit_run(run.id)
            return jsonify({
                'success': True,
                'run_id': run.id,
                'warnings': validation_result.get('warnings', [])
            })
        else:
            return jsonify({'success': False, 'error': 'Ошибка сохранения файлов'}), 500
            
    except Exception as e:
        logging.error(f"Upload error: {str(e)}")
        return jsonify({'success': False, 'error': f'Внутренняя ошибка сервера: {str(e)}'}), 500


@api_bp.route('/<int:run_id>/status')
@login_required
@run_ownership_required
def status(run_id):  # TODO: replace on WebSockets or Long Polling
    run = Run.query.get(run_id)
    
    if not run or run.session_id != session['session_id']:
        return jsonify({'error': 'Run not found'}), 404
    
    result_dict = run.to_dict()
    result_dict.pop('log_content')
    return jsonify(result_dict)


@api_bp.route('/<int:run_id>/logs')
@login_required
@run_ownership_required
def logs(run_id):
    run = Run.query.get(run_id)
    
    if not run:
        return jsonify({'error': 'Run not found'}), 404
    
    return jsonify({
        'id': run.id,
        'status': run.status.value,
        'log_content': run.log_content,
    })


@api_bp.route('/<int:run_id>/download')
@login_required
@run_ownership_required
@run_completed_required
def download_results(run_id):
    from app.models.run import Run
    run = Run.query.get(run_id)
    
    if not run.archive_filename:
        flash('Results archive not available', 'error')
        return redirect(url_for('website.results', run_id=run_id))

    archive_path = os.path.join(RunService.get_project_folder(run_id), run.archive_filename)
    
    if not os.path.exists(archive_path):
        flash('Archive not found', 'error')
        return redirect(url_for('website.results', run_id=run_id))
    
    return send_file(archive_path, as_attachment=True, download_name=run.archive_filename)


@api_bp.route('/<int:run_id>/cancel', methods=['POST'])
@login_required
@run_ownership_required
@run_not_completed_required
def cancel_run(run_id):
    if LibreLaneService.cancel_run(run_id):
        flash('Run cancelled', 'success')
    else:
        flash('Cannot cancel run', 'error')
    
    return redirect(url_for('website.results', run_id=run_id))

