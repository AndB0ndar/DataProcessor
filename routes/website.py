import logging

from flask import Blueprint, render_template


site_bp = Blueprint('website', __name__)

logger = logging.getLogger(__name__)


@site_bp.route('/')
def index():
    return render_template('index.html')


@site_bp.route('/status')
def status():
    return render_template('status.html')


@site_bp.route('/logs')
def logs():
    return render_template('logs.html')


@site_bp.route('/results')
def results():
    return render_template('results.html')


@site_bp.route('/help')
def help():
    return render_template('help.html')

