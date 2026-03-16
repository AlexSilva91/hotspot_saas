from app.extensions import db
from app.models.active_session import ActiveSession
from app.middleware.tenant_middleware import tenant_filter

class ActiveSessionRepository:

    @staticmethod
    def create(data):
        session = ActiveSession(**data)
        db.session.add(session)
        db.session.commit()
        return session

    @staticmethod
    def get_all():
        query = ActiveSession.query
        query = tenant_filter(query)
        return query.all()

    @staticmethod
    def get_by_id(session_id):
        query = ActiveSession.query.filter_by(id=session_id)
        query = tenant_filter(query)
        return query.first()

    @staticmethod
    def delete(session):
        db.session.delete(session)
        db.session.commit()