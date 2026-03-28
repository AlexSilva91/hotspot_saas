from app.services.active_session_service import ActiveSessionService
from app.controller.base_controller import BaseController

class ActiveSessionController:
    
    @staticmethod
    def list():
        """Listar sessões ativas"""
        result = ActiveSessionService.list()
        sessions = result.get("data", [])
        
        return {"sessions": sessions}
    
    @staticmethod
    def disconnect(session_id):
        """Desconectar sessão"""
        result = ActiveSessionService.delete(session_id)
        
        return BaseController.handle_result(
            result=result,
            success_message="Sessão encerrada!",
            error_default="Erro ao encerrar sessão!",
            redirect_to="active_sessions.list_sessions"
        )