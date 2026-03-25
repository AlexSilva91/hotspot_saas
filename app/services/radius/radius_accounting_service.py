from flask import g
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
    def get_tenant_dashboard(cls):
        """Dados para dashboard do tenant"""
        active_sessions = cls.repository.get_active_sessions()
        today_sessions = cls.repository.get_tenant_usage_today()

        # Calcula tráfego de hoje
        today_input = sum(s.acctinputoctets or 0 for s in today_sessions)
        today_output = sum(s.acctoutputoctets or 0 for s in today_sessions)

        return {
            "success": True,
            "data": {
                "active_sessions_count": len(active_sessions),
                "today_sessions_count": len(today_sessions),
                "today_traffic_mb": round((today_input + today_output) / (1024 * 1024), 2),
                "active_sessions": [s.to_dict() for s in active_sessions[:10]]  # Top 10
            }
        }

    @classmethod
    def cleanup_old_sessions(cls, days=90):
        """Limpa sessões antigas"""
        count = cls.repository.cleanup_old_sessions(days)
        return {"success": True, "deleted_count": count}