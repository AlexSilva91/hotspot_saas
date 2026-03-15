from app.repositories.active_session_repository import ActiveSessionRepository


class ActiveSessionService:


    @staticmethod
    def create_session(data):

        return ActiveSessionRepository.create(data)


    @staticmethod
    def list_sessions():

        return ActiveSessionRepository.get_all()


    @staticmethod
    def get_session(session_id):

        session = ActiveSessionRepository.get_by_id(session_id)

        if not session:
            raise Exception("Sessão não encontrada")

        return session


    @staticmethod
    def delete_session(session_id):

        session = ActiveSessionRepository.get_by_id(session_id)

        if not session:
            raise Exception("Sessão não encontrada")

        ActiveSessionRepository.delete(session)