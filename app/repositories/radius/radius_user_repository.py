from app.models.radius.radius_user import RadiusUser
from app.repositories.base_repository import BaseRepository
from app.middleware.tenant_middleware import tenant_filter
from flask import has_request_context
from app.extensions import db


class RadiusUserRepository(BaseRepository):
    model = RadiusUser

    @classmethod
    def _apply_tenant_filter(cls, query):
        """Aplica filtro de tenant apenas se estiver em contexto de requisição"""
        if has_request_context():
            return tenant_filter(query)
        return query

    @classmethod
    def get_by_username(cls, username):
        """Busca um usuário RADIUS pelo nome"""
        query = cls.model.query.filter_by(username=username)
        return query.first()

    @classmethod
    def get_by_username_and_attribute(cls, username, attribute):
        """Busca por username e attribute específico"""
        query = cls.model.query.filter_by(
            username=username,
            attribute=attribute
        )
        return query.first()

    @classmethod
    def get_all(cls):
        """Lista todos os usuários RADIUS"""
        return cls.model.query.all()

    @classmethod
    def get_by_id(cls, obj_id):
        """Busca por ID"""
        return cls.model.query.filter_by(id=obj_id).first()

    @classmethod
    def delete_by_username(cls, username):
        """Remove todos os registros de um usuário"""
        query = cls.model.query.filter_by(username=username)
        count = query.delete()
        db.session.commit()
        return count

    @classmethod
    def get_user_with_rate_limit(cls, username):
        """Retorna usuário com seu rate limit (se existir)"""
        user = cls.get_by_username(username)
        if user:
            from app.repositories.radius.radius_reply_repository import RadiusReplyRepository
            rate_limit = RadiusReplyRepository.get_by_username_and_attribute(
                username, "Mikrotik-Rate-Limit"
            )
            return user, rate_limit
        return None, None