# app/repositories/radius/radius_accounting_repository.py
from app.models.radius.radius_accounting import RadiusAccounting
from app.repositories.base_repository import BaseRepository
from app.middleware.tenant_middleware import tenant_filter
from flask import has_request_context, g
from datetime import datetime, timedelta
from app.extensions import db
from sqlalchemy import func, and_


class RadiusAccountingRepository(BaseRepository):
    model = RadiusAccounting

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
    def get_all(cls):
        """Lista todas as sessões com filtro de tenant"""
        tenant_id = cls._get_tenant_id()
        
        if tenant_id:
            return cls.model.query.filter_by(tenant_id=tenant_id).all()
        return cls.model.query.all()

    @classmethod
    def get_active_sessions(cls):
        """Retorna todas as sessões ativas (sem acctstoptime)"""
        tenant_id = cls._get_tenant_id()
        
        query = cls.model.query.filter(
            RadiusAccounting.acctstoptime.is_(None)
        ).order_by(RadiusAccounting.acctstarttime.desc())
        
        if tenant_id:
            query = query.filter_by(tenant_id=tenant_id)
        
        return query.all()

    @classmethod
    def get_active_sessions_count(cls):
        """Retorna número de sessões ativas"""
        tenant_id = cls._get_tenant_id()
        
        query = cls.model.query.filter(
            RadiusAccounting.acctstoptime.is_(None)
        )
        
        if tenant_id:
            query = query.filter_by(tenant_id=tenant_id)
        
        return query.count()

    @classmethod
    def get_sessions_by_user(cls, username, limit=100):
        """Retorna histórico de sessões de um usuário específico"""
        tenant_id = cls._get_tenant_id()
        
        query = cls.model.query.filter_by(username=username).order_by(
            RadiusAccounting.acctstarttime.desc()
        ).limit(limit)
        
        if tenant_id:
            query = query.filter_by(tenant_id=tenant_id)
        
        return query.all()

    @classmethod
    def get_sessions_by_date_range(cls, start_date, end_date, username=None):
        """Retorna sessões em um intervalo de datas"""
        tenant_id = cls._get_tenant_id()
        
        query = cls.model.query.filter(
            RadiusAccounting.acctstarttime >= start_date,
            RadiusAccounting.acctstarttime <= end_date
        )
        
        if username:
            query = query.filter_by(username=username)
        
        if tenant_id:
            query = query.filter_by(tenant_id=tenant_id)
        
        return query.order_by(RadiusAccounting.acctstarttime.desc()).all()

    @classmethod
    def get_user_usage_summary(cls, username):
        """Resumo de uso de um usuário (tempo total, tráfego total)"""
        tenant_id = cls._get_tenant_id()
        
        query = cls.model.query.filter_by(username=username)
        
        if tenant_id:
            query = query.filter_by(tenant_id=tenant_id)

        result = query.with_entities(
            func.sum(RadiusAccounting.acctsessiontime).label('total_time'),
            func.sum(RadiusAccounting.acctinputoctets).label('total_input'),
            func.sum(RadiusAccounting.acctoutputoctets).label('total_output'),
            func.count(RadiusAccounting.radacctid).label('session_count')
        ).first()

        return {
            'total_time': result.total_time or 0,
            'total_time_hours': round((result.total_time or 0) / 3600, 2),
            'total_input': result.total_input or 0,
            'total_output': result.total_output or 0,
            'total_traffic': (result.total_input or 0) + (result.total_output or 0),
            'total_input_mb': round((result.total_input or 0) / (1024 * 1024), 2),
            'total_output_mb': round((result.total_output or 0) / (1024 * 1024), 2),
            'total_traffic_mb': round(((result.total_input or 0) + (result.total_output or 0)) / (1024 * 1024), 2),
            'session_count': result.session_count or 0
        }

    @classmethod
    def get_today_traffic(cls):
        """Retorna tráfego de hoje"""
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        tenant_id = cls._get_tenant_id()
        
        query = cls.model.query.filter(
            RadiusAccounting.acctstarttime >= today
        )
        
        if tenant_id:
            query = query.filter_by(tenant_id=tenant_id)
        
        result = query.with_entities(
            func.sum(RadiusAccounting.acctinputoctets).label('input'),
            func.sum(RadiusAccounting.acctoutputoctets).label('output')
        ).first()
        
        return {
            'input': result.input or 0,
            'output': result.output or 0,
            'input_mb': round((result.input or 0) / (1024 * 1024), 2),
            'output_mb': round((result.output or 0) / (1024 * 1024), 2),
            'total_mb': round(((result.input or 0) + (result.output or 0)) / (1024 * 1024), 2)
        }

    @classmethod
    def cleanup_old_sessions(cls, days=90):
        """Remove sessões mais antigas que X dias"""
        cutoff = datetime.now() - timedelta(days=days)
        tenant_id = cls._get_tenant_id()
        
        query = cls.model.query.filter(
            and_(
                RadiusAccounting.acctstarttime < cutoff,
                RadiusAccounting.acctstoptime.isnot(None)
            )
        )
        
        if tenant_id:
            query = query.filter_by(tenant_id=tenant_id)
        
        count = query.delete()
        db.session.commit()
        return count
    
    @classmethod
    def get_all_by_tenant(cls, tenant_id):
        """Retorna todas as sessões de um tenant específico (usado em CLI)"""
        return cls.model.query.filter_by(tenant_id=tenant_id).all()

    @classmethod
    def get_user_current_session(cls, username):
        """Retorna a sessão atual de um usuário se estiver online"""
        tenant_id = cls._get_tenant_id()
        
        query = cls.model.query.filter(
            and_(
                RadiusAccounting.username == username,
                RadiusAccounting.acctstoptime.is_(None)
            )
        )
        
        if tenant_id:
            query = query.filter_by(tenant_id=tenant_id)
        
        return query.first()