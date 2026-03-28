# app/services/radius/radius_postauth_service.py (NOVO)
from app.services.base_service import BaseService
from app.repositories.radius.radius_postauth_repository import RadiusPostAuthRepository


class RadiusPostAuthService(BaseService):
    repository = RadiusPostAuthRepository
    not_found_message = "Registro de autenticação não encontrado"

    @classmethod
    def get_last_auth_attempts(cls, username=None, limit=50):
        """Retorna últimas tentativas de autenticação"""
        attempts = cls.repository.get_last_auth_attempts(username, limit)
        return {"success": True, "data": attempts}

    @classmethod
    def get_failed_attempts(cls, username=None, since_hours=24):
        """Retorna tentativas falhas"""
        attempts = cls.repository.get_failed_attempts(username, since_hours)
        return {"success": True, "data": attempts}

    @classmethod
    def get_successful_attempts(cls, username=None, since_hours=24):
        """Retorna tentativas bem-sucedidas"""
        attempts = cls.repository.get_successful_attempts(username, since_hours)
        return {"success": True, "data": attempts}