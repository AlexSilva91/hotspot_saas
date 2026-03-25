from app.models.radius.radius_user import RadiusUser
from app.repositories.base_repository import BaseRepository
from app.middleware.tenant_middleware import tenant_filter
from flask import g, has_request_context
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
        """Busca um usuário RADIUS pelo nome, respeitando tenant apenas em contexto web"""
        query = cls.model.query.filter_by(username=username)
        query = cls._apply_tenant_filter(query)
        return query.first()

    @classmethod
    def get_by_username_and_attribute(cls, username, attribute):
        """Busca por username e attribute específico"""
        query = cls.model.query.filter_by(
            username=username,
            attribute=attribute
        )
        query = cls._apply_tenant_filter(query)
        return query.first()

    @classmethod
    def get_all(cls):
        """Lista todos os usuários RADIUS com filtro de tenant apenas em contexto web"""
        query = cls.model.query
        query = cls._apply_tenant_filter(query)
        return query.all()

    @classmethod
    def get_all_by_tenant(cls, tenant_id):
        """Lista todos os usuários de um tenant específico (usado em CLI)"""
        return cls.model.query.filter_by(tenant_id=tenant_id).all()

    @classmethod
    def get_by_id(cls, obj_id):
        """Busca por ID com filtro de tenant apenas em contexto web"""
        query = cls.model.query.filter_by(id=obj_id)
        query = cls._apply_tenant_filter(query)
        return query.first()

    @classmethod
    def delete_by_username(cls, username):
        """Remove todos os registros de um usuário"""
        query = cls.model.query.filter_by(username=username)
        query = cls._apply_tenant_filter(query)
        count = query.delete()
        db.session.commit()
        return count