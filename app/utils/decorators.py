from functools import wraps

from flask import flash, redirect, url_for, session

from app.models.session import Session
from app.models.run import Run, RunStatus
from app.services.run_service import RunService
from app.services.auth_service import AuthService


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'session_id' not in session:
            flash('Please log in first', 'error')
            return redirect(url_for('auth.email_login'))
        
        session_obj = Session.query.get(session['session_id'])
        if not session_obj or not session_obj.is_valid():
            session.clear()
            flash('Session expired, please log in again', 'error')
            return redirect(url_for('auth.email_login'))
        
        return f(*args, **kwargs)
    return decorated_function


def no_active_run_required(f):
    """Denies access if there is an active startup"""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if RunService.has_active_run(session['session_id']):
            active_run = RunService.get_active_run(session['session_id'])
            flash('You already have an active run. Please wait for it to complete.', 'warning')
            return redirect(url_for('website.status', run_id=active_run.id))
        return f(*args, **kwargs)
    return decorated_function


def run_ownership_required(f):
    """Checks that the startup is owned by the user"""
    @wraps(f)
    @login_required
    def decorated_function(run_id, *args, **kwargs):
        run = Run.query.get(run_id)
        
        if not run or run.session_id != session['session_id']:
            flash('Run not found or access denied', 'error')
            return redirect(url_for('website.upload'))
        
        return f(run_id, *args, **kwargs)
    return decorated_function


def run_completed_required(f):
    """Requires a completed launch"""
    @wraps(f)
    @run_ownership_required
    def decorated_function(run_id, *args, **kwargs):
        run = Run.query.get(run_id)
        
        if run.status != RunStatus.COMPLETED:
            flash('Run is not completed yet', 'error')
            return redirect(url_for('website.status', run_id=run_id))
        
        return f(run_id, *args, **kwargs)
    return decorated_function


def run_not_completed_required(f):
    """Requires an unfinished launch"""
    @wraps(f)
    @run_ownership_required
    def decorated_function(run_id, *args, **kwargs):
        run = Run.query.get(run_id)
        
        if run.status in [RunStatus.COMPLETED, RunStatus.FAILED, RunStatus.CANCELLED]:
            flash('Run is already completed', 'error')
            return redirect(url_for('website.results', run_id=run_id))
        
        return f(run_id, *args, **kwargs)
    return decorated_function

