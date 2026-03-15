from app.extensions import db
from app.models.active_session import ActiveSession


class ActiveSessionRepository:


    @staticmethod
    def create(data):

        session = ActiveSession(**data)

        db.session.add(session)
        db.session.commit()

        return session


    @staticmethod
    def get_all():

        return ActiveSession.query.all()


    @staticmethod
    def get_by_id(session_id):

        return ActiveSession.query.get(session_id)


    @staticmethod
    def delete(session):

        db.session.delete(session)
        db.session.commit()