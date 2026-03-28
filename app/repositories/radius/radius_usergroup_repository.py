# app/repositories/radius/radius_usergroup_repository.py
from app.models.radius.radius_usergroup import RadiusUserGroup
from app.repositories.base_repository import BaseRepository
from flask import has_request_context, g
from app.extensions import db


class RadiusUserGroupRepository(BaseRepository):
    model = RadiusUserGroup

    @classmethod
    def _get_tenant_id(cls):
        """Retorna tenant_id do usuário logado"""
        if has_request_context() and hasattr(g, 'current_user') and g.current_user:
            return g.current_user.tenant_id
        return None

    @classmethod
    def get_by_username(cls, username):
        """Retorna grupos de um usuário"""
        tenant_id = cls._get_tenant_id()
        
        query = cls.model.query.filter_by(username=username)
        if tenant_id:
            query = query.filter_by(tenant_id=tenant_id)
        
        return query.all()

    @classmethod
    def add_user_to_group(cls, username, groupname, priority=1):
        """Adiciona usuário a um grupo"""
        tenant_id = cls._get_tenant_id()
        
        existing = cls.model.query.filter_by(
            username=username,
            groupname=groupname
        ).first()
        
        if existing:
            return existing
        
        new_assoc = cls.model(
            username=username,
            groupname=groupname,
            priority=priority,
            tenant_id=tenant_id
        )
        db.session.add(new_assoc)
        db.session.commit()
        return new_assoc

    @classmethod
    def remove_user_from_group(cls, username, groupname):
        """Remove usuário de um grupo"""
        tenant_id = cls._get_tenant_id()
        
        query = cls.model.query.filter_by(
            username=username,
            groupname=groupname
        )
        
        if tenant_id:
            query = query.filter_by(tenant_id=tenant_id)
        
        count = query.delete()
        db.session.commit()
        return count