from app.services.base_service import BaseService
from app.repositories.active_session_repository import ActiveSessionRepository


class ActiveSessionService(BaseService):
    repository = ActiveSessionRepository
    not_found_message = "Sessão não encontrada"

