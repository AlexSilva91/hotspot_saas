from app.models.radius.radius_reply import RadiusReply
from app.repositories.base_repository import BaseRepository
from app.middleware.tenant_middleware import tenant_filter
from flask import has_request_context
from app.extensions import db

class RadiusReplyRepository(BaseRepository):
    model = RadiusReply

    @classmethod
    def _apply_tenant_filter(cls, query):
        """Aplica filtro de tenant apenas se estiver em contexto de requisição"""
        if has_request_context():
            return tenant_filter(query)
        return query

    @classmethod
    def get_by_username(cls, username):
        """Busca todos os atributos de um usuário"""
        query = cls.model.query.filter_by(username=username)
        query = cls._apply_tenant_filter(query)
        return query.all()

    @classmethod
    def get_by_username_and_attribute(cls, username, attribute):
        """Busca um atributo específico de um usuário"""
        query = cls.model.query.filter_by(
            username=username,
            attribute=attribute
        )
        query = cls._apply_tenant_filter(query)
        return query.first()

    @classmethod
    def get_all(cls):
        """Lista todos os atributos com filtro de tenant apenas em contexto web"""
        query = cls.model.query
        query = cls._apply_tenant_filter(query)
        return query.all()

    @classmethod
    def delete_by_username(cls, username):
        """Remove todos os atributos de um usuário"""
        query = cls.model.query.filter_by(username=username)
        query = cls._apply_tenant_filter(query)
        count = query.delete()
        db.session.commit()
        return count