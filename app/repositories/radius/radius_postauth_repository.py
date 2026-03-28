# app/repositories/radius/radius_postauth_repository.py
from app.models.radius.radius_postauth import RadiusPostAuth
from app.repositories.base_repository import BaseRepository
from app.middleware.tenant_middleware import tenant_filter
from flask import has_request_context, g
from datetime import datetime, timedelta
from app.extensions import db


class RadiusPostAuthRepository(BaseRepository):
    model = RadiusPostAuth

    @classmethod
    def _apply_tenant_filter(cls, query):
        """Aplica filtro de tenant apenas se estiver em contexto de requisição"""
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
    def get_last_auth_attempts(cls, username=None, limit=50):
        """Retorna as últimas tentativas de autenticação"""
        tenant_id = cls._get_tenant_id()
        
        query = cls.model.query.order_by(
            RadiusPostAuth.authdate.desc()
        ).limit(limit)
        
        if username:
            query = query.filter_by(username=username)
        
        if tenant_id:
            query = query.filter_by(tenant_id=tenant_id)
        
        return query.all()

    @classmethod
    def get_failed_attempts(cls, username=None, since_hours=24):
        """Retorna tentativas de autenticação falhas nas últimas X horas"""
        since = datetime.now() - timedelta(hours=since_hours)
        tenant_id = cls._get_tenant_id()
        
        query = cls.model.query.filter(
            RadiusPostAuth.authdate >= since,
            RadiusPostAuth.reply == 'Access-Reject'
        )
        
        if username:
            query = query.filter_by(username=username)
        
        if tenant_id:
            query = query.filter_by(tenant_id=tenant_id)
        
        return query.all()

    @classmethod
    def get_successful_attempts(cls, username=None, since_hours=24):
        """Retorna tentativas de autenticação bem-sucedidas nas últimas X horas"""
        since = datetime.now() - timedelta(hours=since_hours)
        tenant_id = cls._get_tenant_id()
        
        query = cls.model.query.filter(
            RadiusPostAuth.authdate >= since,
            RadiusPostAuth.reply == 'Access-Accept'
        )
        
        if username:
            query = query.filter_by(username=username)
        
        if tenant_id:
            query = query.filter_by(tenant_id=tenant_id)
        
        return query.all()