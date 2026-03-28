# app/repositories/radius/radius_user_repository.py
from app.models.radius.radius_user import RadiusUser
from app.repositories.base_repository import BaseRepository
from app.middleware.tenant_middleware import tenant_filter
from flask import has_request_context, g
from app.extensions import db


class RadiusUserRepository(BaseRepository):
    model = RadiusUser

    @classmethod
    def _apply_tenant_filter(cls, query):
        """Aplica filtro de tenant"""
        if has_request_context():
            return tenant_filter(query)
        return query

    @classmethod
    def _get_tenant_id(cls):
        """Retorna tenant_id do usuário logado"""
        if has_request_context() and hasattr(g, 'current_user') and g.current_user:
            return g.current_user.tenant_id
        return None

    @classmethod
    def get_by_username(cls, username):
        """Busca um usuário RADIUS pelo nome (considerando tenant)"""
        tenant_id = cls._get_tenant_id()
        
        if tenant_id:
            # Busca direta com tenant_id (MAIS RÁPIDO)
            return cls.model.query.filter_by(
                username=username,
                tenant_id=tenant_id
            ).first()
        
        # Fallback: busca sem tenant (CLI)
        return cls.model.query.filter_by(username=username).first()

    @classmethod
    def get_by_username_and_attribute(cls, username, attribute):
        """Busca por username e attribute específico"""
        tenant_id = cls._get_tenant_id()
        
        query = cls.model.query.filter_by(
            username=username,
            attribute=attribute
        )
        
        if tenant_id:
            query = query.filter_by(tenant_id=tenant_id)
        
        return query.first()

    @classmethod
    def get_all(cls):
        """Lista todos os usuários RADIUS do tenant"""
        query = cls.model.query
        query = cls._apply_tenant_filter(query)
        return query.all()

    @classmethod
    def get_active_users(cls):
        """Lista apenas usuários ativos"""
        query = cls.model.query.filter_by(is_active=True)
        query = cls._apply_tenant_filter(query)
        return query.all()

    @classmethod
    def create(cls, data):
        """Cria um novo usuário no radcheck"""
        # Define valores padrão
        if 'attribute' not in data:
            data['attribute'] = 'Cleartext-Password'
        if 'op' not in data:
            data['op'] = ':='
        
        # Adiciona tenant_id automaticamente
        tenant_id = cls._get_tenant_id()
        if tenant_id:
            data['tenant_id'] = tenant_id
        elif 'tenant_id' not in data:
            # Se não tem tenant_id em lugar nenhum, erro
            raise ValueError("tenant_id é obrigatório para criar usuário RADIUS")
        
        return super().create(data)

    @classmethod
    def update_active_status(cls, username, is_active):
        """Atualiza status ativo/inativo do usuário"""
        user = cls.get_by_username(username)
        if user:
            user.is_active = is_active
            db.session.commit()
            return user
        return None

    @classmethod
    def block_user(cls, username):
        """Bloqueia um usuário"""
        return cls.update_active_status(username, False)

    @classmethod
    def unblock_user(cls, username):
        """Desbloqueia um usuário"""
        return cls.update_active_status(username, True)

    @classmethod
    def delete_by_username(cls, username):
        """Remove todos os registros de um usuário"""
        tenant_id = cls._get_tenant_id()
        
        query = cls.model.query.filter_by(username=username)
        if tenant_id:
            query = query.filter_by(tenant_id=tenant_id)
        
        count = query.delete()
        db.session.commit()
        return count

    @classmethod
    def count_by_tenant(cls):
        """Conta usuários do tenant atual"""
        tenant_id = cls._get_tenant_id()
        if tenant_id:
            return cls.model.query.filter_by(tenant_id=tenant_id).count()
        return cls.model.query.count()