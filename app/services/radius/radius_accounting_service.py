from flask import g, current_app
from app.services.base_service import BaseService
from app.repositories.radius.radius_accounting_repository import RadiusAccountingRepository
from datetime import datetime, timedelta

class RadiusAccountingService(BaseService):
    repository = RadiusAccountingRepository
    not_found_message = "Sessão não encontrada"

    @classmethod
    def get_active_sessions(cls):
        """Retorna sessões ativas com informações enriquecidas"""
        sessions = cls.repository.get_active_sessions()
        # Enriquecer com dados do router/tenant se necessário
        return {"success": True, "data": sessions}

    @classmethod
    def get_active_sessions_count(cls):
        """Retorna número de sessões ativas"""
        count = cls.repository.get_active_sessions_count()
        return {"success": True, "data": count}

    @classmethod
    def get_user_history(cls, username, limit=100):
        """Retorna histórico de sessões de um usuário"""
        sessions = cls.repository.get_sessions_by_user(username, limit)
        return {"success": True, "data": sessions}

    @classmethod
    def get_user_summary(cls, username):
        """Retorna resumo de uso de um usuário"""
        summary = cls.repository.get_user_usage_summary(username)
        # Converte bytes para formatos legíveis
        summary['total_input_mb'] = round(summary['total_input'] / (1024 * 1024), 2)
        summary['total_output_mb'] = round(summary['total_output'] / (1024 * 1024), 2)
        summary['total_traffic_mb'] = round(summary['total_input_mb'] + summary['total_output_mb'], 2)
        summary['total_time_hours'] = round(summary['total_time'] / 3600, 2)
        return {"success": True, "data": summary}

    @classmethod
    def get_today_traffic(cls):
        """Retorna tráfego de hoje"""
        traffic = cls.repository.get_today_traffic()
        return {"success": True, "data": traffic}

    @classmethod
    def get_tenant_dashboard(cls):
        """Dados para dashboard do tenant"""
        active_sessions = cls.repository.get_active_sessions()
        today_traffic = cls.repository.get_today_traffic()
        active_count = cls.repository.get_active_sessions_count()

        return {
            "success": True,
            "data": {
                "active_sessions_count": active_count,
                "today_traffic_mb": today_traffic['total_mb'],
                "active_sessions": [s.to_dict() for s in active_sessions[:10]]
            }
        }

    @classmethod
    def get_user_current_session(cls, username):
        """Retorna a sessão atual de um usuário"""
        session = cls.repository.get_user_current_session(username)
        return {"success": True, "data": session}

    @classmethod
    def cleanup_old_sessions(cls, days=90):
        """Limpa sessões antigas"""
        count = cls.repository.cleanup_old_sessions(days)
        return {"success": True, "deleted_count": count}