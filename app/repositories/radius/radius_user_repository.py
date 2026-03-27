# app/repositories/radius/radius_user_repository.py

from app.models.radius.radius_user import RadiusUser
from app.repositories.base_repository import BaseRepository
from app.middleware.tenant_middleware import tenant_filter
from flask import has_request_context, g
from app.extensions import db
from app.services.radius.tenant_prefix_service import TenantPrefixService


class RadiusUserRepository(BaseRepository):
    model = RadiusUser

    @classmethod
    def _apply_tenant_filter(cls, query):
        """Aplica filtro de tenant apenas se estiver em contexto de requisição"""
        if has_request_context():
            return tenant_filter(query)
        return query

    @classmethod
    def _encode_username(cls, username):
        """Adiciona prefixo ao username se necessário (apenas para não-admin)"""
        if has_request_context() and hasattr(g, 'current_user') and g.current_user:
            if g.current_user.role.value not in ["ADMIN", "MANAGER"]:
                if TenantPrefixService.SEPARATOR not in username:
                    return TenantPrefixService.encode(username)
        return username

    @classmethod
    def get_by_username(cls, username):
        """Busca um usuário RADIUS pelo nome"""
        username = cls._encode_username(username)
        query = cls.model.query.filter_by(username=username)
        return query.first()

    @classmethod
    def get_by_username_and_attribute(cls, username, attribute):
        """Busca por username e attribute específico"""
        username = cls._encode_username(username)
        query = cls.model.query.filter_by(
            username=username,
            attribute=attribute
        )
        return query.first()

    @classmethod
    def get_all(cls):
        """Lista todos os usuários RADIUS"""
        query = cls.model.query
        query = cls._apply_tenant_filter(query)
        return query.all()

    @classmethod
    def get_by_id(cls, obj_id):
        """Busca por ID"""
        return cls.model.query.filter_by(id=obj_id).first()

    @classmethod
    def create(cls, data):
        """Cria um novo usuário no radcheck"""
        # Define valores padrão
        if 'attribute' not in data:
            data['attribute'] = 'Cleartext-Password'
        if 'op' not in data:
            data['op'] = ':='
        
        username = data.get('username')
        
        # Adiciona prefixo se necessário
        if has_request_context() and hasattr(g, 'current_user') and g.current_user:
            if g.current_user.role.value not in ["ADMIN", "MANAGER"]:
                if TenantPrefixService.SEPARATOR not in username:
                    data['username'] = TenantPrefixService.encode(username)
        
        return super().create(data)

    @classmethod
    def delete_by_username(cls, username):
        """Remove todos os registros de um usuário"""
        username = cls._encode_username(username)
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