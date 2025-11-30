import logging

from flask import Blueprint
from flask import flash, redirect, render_template, request, session, url_for, jsonify

from app.utils.decorators import (
    login_required, 
    no_active_run_required, 
    run_ownership_required,
    run_completed_required,
    run_not_completed_required,
)
from app.services.run_service import RunService
from app.services.librelane_service import LibreLaneService


site_bp = Blueprint('website', __name__)

logger = logging.getLogger(__name__)


@site_bp.route('/help')
def help():
    return render_template('pages/help.html')


@site_bp.route('/upload')
@login_required
@no_active_run_required
def upload():
    return render_template('pages/upload.html')


@site_bp.route('/<int:run_id>')
@login_required
@run_ownership_required
def status(run_id):
    from app.models.run import Run
    run = Run.query.get(run_id)

    if not run or run.session_id != session['session_id']:
        flash('Run not found', 'error')
        return redirect(url_for('website.upload'))
    
    return render_template('pages/status.html', run=run)


@site_bp.route('/<int:run_id>/logs')
@login_required
@run_ownership_required
def logs(run_id):
    from app.models.run import Run
    run = Run.query.get(run_id)
    return render_template('pages/logs.html', run=run)


@site_bp.route('/<int:run_id>/results')
@login_required
@run_ownership_required
@run_completed_required
def results(run_id):
    from app.models.run import Run
    run = Run.query.get(run_id)

    if not run or run.session_id != session['session_id']:
        flash('Run not found', 'error')
        return redirect(url_for('website.upload'))

    return render_template('pages/results.html', run=run)

