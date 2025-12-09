import sys
sys.path.insert(0, '.')

from run import app, db
import os

with app.app_context():
    db.create_all()
    print("Database initialized")

