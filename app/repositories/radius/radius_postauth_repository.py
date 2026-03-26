from app.models.radius.radius_postauth import RadiusPostAuth
from app.repositories.base_repository import BaseRepository
from app.middleware.tenant_middleware import tenant_filter
from flask import has_request_context
from datetime import datetime
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
    def get_last_auth_attempts(cls, username=None, limit=50):
        """Retorna as últimas tentativas de autenticação"""
        query = cls.model.query.order_by(
            RadiusPostAuth.authdate.desc()
        ).limit(limit)
        
        if username:
            query = query.filter_by(username=username)
        
        query = cls._apply_tenant_filter(query)
        return query.all()

    @classmethod
    def get_failed_attempts(cls, username=None, since_hours=24):
        """Retorna tentativas de autenticação falhas nas últimas X horas"""
        since = datetime.now() - timedelta(hours=since_hours)
        query = cls.model.query.filter(
            RadiusPostAuth.authdate >= since,
            RadiusPostAuth.reply == 'Access-Reject'
        )
        
        if username:
            query = query.filter_by(username=username)
        
        query = cls._apply_tenant_filter(query)
        return query.all()

    @classmethod
    def get_successful_attempts(cls, username=None, since_hours=24):
        """Retorna tentativas de autenticação bem-sucedidas nas últimas X horas"""
        since = datetime.now() - timedelta(hours=since_hours)
        query = cls.model.query.filter(
            RadiusPostAuth.authdate >= since,
            RadiusPostAuth.reply == 'Access-Accept'
        )
        
        if username:
            query = query.filter_by(username=username)
        
        query = cls._apply_tenant_filter(query)
        return query.all()