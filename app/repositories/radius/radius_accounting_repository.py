from app.models.radius.radius_accounting import RadiusAccounting
from app.repositories.base_repository import BaseRepository
from app.middleware.tenant_middleware import tenant_filter
from flask import has_request_context
from datetime import datetime, timedelta
from app.extensions import db
from sqlalchemy import func

class RadiusAccountingRepository(BaseRepository):
    model = RadiusAccounting

    @classmethod
    def _apply_tenant_filter(cls, query):
        """Aplica filtro de tenant apenas se estiver em contexto de requisição"""
        if has_request_context():
            return tenant_filter(query)
        return query

    @classmethod
    def get_all(cls):
        """Lista todas as sessões com filtro de tenant apenas em contexto web"""
        query = cls.model.query
        query = cls._apply_tenant_filter(query)
        return query.all()

    @classmethod
    def get_active_sessions(cls):
        """Retorna todas as sessões ativas (sem acctstoptime)"""
        query = cls.model.query.filter(
            RadiusAccounting.acctstoptime.is_(None)
        ).order_by(RadiusAccounting.acctstarttime.desc())
        query = cls._apply_tenant_filter(query)
        return query.all()

    @classmethod
    def get_sessions_by_user(cls, username, limit=100):
        """Retorna histórico de sessões de um usuário específico"""
        query = cls.model.query.filter_by(username=username).order_by(
            RadiusAccounting.acctstarttime.desc()
        ).limit(limit)
        query = cls._apply_tenant_filter(query)
        return query.all()

    @classmethod
    def get_sessions_by_date_range(cls, start_date, end_date, username=None):
        """Retorna sessões em um intervalo de datas"""
        query = cls.model.query.filter(
            RadiusAccounting.acctstarttime >= start_date,
            RadiusAccounting.acctstarttime <= end_date
        )
        if username:
            query = query.filter_by(username=username)
        query = cls._apply_tenant_filter(query)
        return query.order_by(RadiusAccounting.acctstarttime.desc()).all()

    @classmethod
    def get_user_usage_summary(cls, username):
        """Resumo de uso de um usuário (tempo total, tráfego total)"""
        query = cls.model.query.filter_by(username=username)
        query = cls._apply_tenant_filter(query)

        result = query.with_entities(
            func.sum(RadiusAccounting.acctsessiontime).label('total_time'),
            func.sum(RadiusAccounting.acctinputoctets).label('total_input'),
            func.sum(RadiusAccounting.acctoutputoctets).label('total_output'),
            func.count(RadiusAccounting.radacctid).label('session_count')
        ).first()

        return {
            'total_time': result.total_time or 0,
            'total_input': result.total_input or 0,
            'total_output': result.total_output or 0,
            'session_count': result.session_count or 0
        }

    @classmethod
    def get_tenant_usage_today(cls):
        """Retorna uso total do tenant hoje (apenas em contexto web)"""
        if not has_request_context():
            return []
        
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        query = cls.model.query.filter(
            RadiusAccounting.acctstarttime >= today
        )
        return tenant_filter(query).all()

    @classmethod
    def cleanup_old_sessions(cls, days=90):
        """Remove sessões mais antigas que X dias"""
        cutoff = datetime.now() - timedelta(days=days)
        query = cls.model.query.filter(
            RadiusAccounting.acctstarttime < cutoff,
            RadiusAccounting.acctstoptime.isnot(None)
        )
        # Não aplica tenant_filter na limpeza para garantir que remove todas
        count = query.delete()
        db.session.commit()
        return count
    
    @classmethod
    def get_all_by_tenant(cls, tenant_id):
        """Retorna todas as sessões de um tenant específico (usado em CLI)"""
        return cls.model.query.filter_by(tenant_id=tenant_id).all()