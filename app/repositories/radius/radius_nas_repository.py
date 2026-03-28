# app/repositories/radius/radius_nas_repository.py
from app.models.radius.radius_nas import RadiusNas
from app.repositories.base_repository import BaseRepository
from flask import has_request_context, g
from app.extensions import db


class RadiusNasRepository(BaseRepository):
    model = RadiusNas

    @classmethod
    def _get_tenant_id(cls):
        """Retorna tenant_id do usuário logado"""
        if has_request_context() and hasattr(g, 'current_user') and g.current_user:
            return g.current_user.tenant_id
        return None

    @classmethod
    def get_by_nasname(cls, nasname):
        """Busca NAS por nome/IP"""
        tenant_id = cls._get_tenant_id()
        
        query = cls.model.query.filter_by(nasname=nasname)
        if tenant_id:
            query = query.filter_by(tenant_id=tenant_id)
        
        return query.first()

    @classmethod
    def get_all(cls):
        """Lista todos os NAS do tenant"""
        tenant_id = cls._get_tenant_id()
        
        if tenant_id:
            return cls.model.query.filter_by(tenant_id=tenant_id).all()
        return cls.model.query.all()

    @classmethod
    def create(cls, data):
        """Cria um novo NAS"""
        tenant_id = cls._get_tenant_id()
        if tenant_id:
            data['tenant_id'] = tenant_id
        
        return super().create(data)

    @classmethod
    def update_secret(cls, nasname, new_secret):
        """Atualiza o secret de um NAS"""
        nas = cls.get_by_nasname(nasname)
        if nas:
            nas.secret = new_secret
            db.session.commit()
            return nas
        return None