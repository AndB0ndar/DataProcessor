import logging

from datetime import timedelta
from flask import Blueprint
from flask import render_template, request, redirect, url_for, flash, session, jsonify, current_app

from app.services.auth_service import AuthService


auth_bp = Blueprint('auth', __name__)

logger = logging.getLogger(__name__)


@auth_bp.route('/', methods=['GET', 'POST'])
def email_login():
    if request.method == 'POST':
        email = request.form.get('email')
        if not email:
            flash('Please enter your email address', 'error')
            return render_template('auth/email_login.html')
        
        # Создаем сессию
        session_obj = AuthService.create_session(email)
        
        # В реальном приложении отправить email с ссылкой
        magic_link = url_for('auth.magic_login', token=session_obj.token, _external=True)

        logger.debug("=" * 60)
        logger.debug(f"MAGIC LINK for {email}:")
        logger.debug(f"{magic_link}")
        logger.debug(f"Expires at: {session_obj.expires_at}")
        logger.debug("=" * 60)
        
        return render_template('auth/email_login.html', magic_link=magic_link)
    
    return render_template('auth/email_login.html')


@auth_bp.route('/login/<token>')
def magic_login(token):
    session_obj = AuthService.validate_session(token)
    if not session_obj:
        flash('Invalid or expired login link', 'error')
        return redirect(url_for('auth.email_login'))
    
    # Устанавливаем сессию
    session['session_id'] = session_obj.id
    session['email'] = session_obj.email
    session.permanent = True

    logger.debug("=" * 50)
    logger.debug(f"USER LOGGED IN:")
    logger.debug(f"Email: {session_obj.email}")
    logger.debug(f"Session ID: {session_obj.id}")
    logger.debug(f"Session expires: {session_obj.expires_at}")
    logger.debug("=" * 50)
    
    flash(f'Welcome! Session valid for 4 hours.', 'success')
    return redirect(url_for('website.upload'))


@auth_bp.route('/logout')
def logout():
    session.clear()

    email = session.get('email')
    if email:
        logger.debug("=" * 40)
        logger.debug(f"USER LOGGED OUT: {email}")
        logger.debug("=" * 40)

    flash('You have been logged out', 'info')
    return redirect(url_for('auth.email_login'))

