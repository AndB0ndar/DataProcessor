import secrets

from datetime import datetime, timedelta

from app import db


class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False, index=True)
    token = db.Column(db.String(32), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    
    def __init__(self, email):
        self.email = email
        self.token = secrets.token_urlsafe(16)
        self.expires_at = datetime.utcnow() + timedelta(hours=4)
    
    def is_valid(self):
        return datetime.utcnow() < self.expires_at
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'token': self.token,
            'expires_at': self.expires_at.isoformat()
        }
