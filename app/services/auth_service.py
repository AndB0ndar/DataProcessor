from app.models.session import Session
from app import db
from datetime import datetime, timedelta
import secrets

class AuthService:
    @staticmethod
    def create_session(email):
        # Очищаем старые сессии для этого email
        Session.query.filter_by(email=email).delete()
        
        session = Session(email=email)
        db.session.add(session)
        db.session.commit()
        
        return session
    
    @staticmethod
    def get_session_by_token(token):
        return Session.query.filter_by(token=token).first()
    
    @staticmethod
    def validate_session(token):
        session = AuthService.get_session_by_token(token)
        if session and session.is_valid():
            return session
        return None
    
    @staticmethod
    def cleanup_expired_sessions():
        expired = Session.query.filter(Session.expires_at < datetime.utcnow()).all()
        for session in expired:
            db.session.delete(session)
        db.session.commit()
    
    @staticmethod
    def get_session_runs(session_id):
        from app.models.run import Run
        return Run.query.filter_by(session_id=session_id).order_by(Run.created_at.desc()).all()
