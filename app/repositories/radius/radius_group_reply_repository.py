# app/repositories/radius/radius_group_reply_repository.py
from app.models.radius.radius_group_reply import RadiusGroupReply
from app.repositories.base_repository import BaseRepository
from flask import has_request_context, g
from app.extensions import db


class RadiusGroupReplyRepository(BaseRepository):
    model = RadiusGroupReply

    @classmethod
    def _get_tenant_id(cls):
        """Retorna tenant_id do usuário logado"""
        if has_request_context() and hasattr(g, 'current_user') and g.current_user:
            return g.current_user.tenant_id
        return None

    @classmethod
    def get_by_group(cls, groupname):
        """Retorna atributos de um grupo"""
        tenant_id = cls._get_tenant_id()
        
        query = cls.model.query.filter_by(groupname=groupname)
        if tenant_id:
            query = query.filter_by(tenant_id=tenant_id)
        
        return query.all()

    @classmethod
    def get_by_group_and_attribute(cls, groupname, attribute):
        """Retorna um atributo específico de um grupo"""
        tenant_id = cls._get_tenant_id()
        
        query = cls.model.query.filter_by(
            groupname=groupname,
            attribute=attribute
        )
        
        if tenant_id:
            query = query.filter_by(tenant_id=tenant_id)
        
        return query.first()

    @classmethod
    def create_or_update(cls, groupname, attribute, value, op=':='):
        """Cria ou atualiza um atributo de grupo"""
        tenant_id = cls._get_tenant_id()
        
        existing = cls.get_by_group_and_attribute(groupname, attribute)
        
        if existing:
            existing.value = value
            existing.op = op
            db.session.commit()
            return existing
        else:
            new_attr = cls.model(
                groupname=groupname,
                attribute=attribute,
                op=op,
                value=value,
                tenant_id=tenant_id
            )
            db.session.add(new_attr)
            db.session.commit()
            return new_attr

    @classmethod
    def delete_by_group(cls, groupname):
        """Remove todos atributos de um grupo"""
        tenant_id = cls._get_tenant_id()
        
        query = cls.model.query.filter_by(groupname=groupname)
        if tenant_id:
            query = query.filter_by(tenant_id=tenant_id)
        
        count = query.delete()
        db.session.commit()
        return count