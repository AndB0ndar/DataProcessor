import os

from app import create_app, db


app = create_app()


def init_app():
    with app.app_context():
        db.create_all()
        
        runs_folder = app.config.get('RUNS_FOLDER', 'runs')
        os.makedirs(runs_folder, exist_ok=True)
        logs_folder = app.config.get('LOG_FOLDER', 'logs')
        os.makedirs(logs_folder, exist_ok=True)
        
        print("Application initialized successfully")


if __name__ == '__main__':
    init_app()
    app.run(
        debug=app.config.get('DEBUG', True),
        host=app.config.get('HOST', '0.0.0.0'),
        port=app.config.get('PORT', 5000)
    )

