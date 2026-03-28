from flask import request
from app.services.hotspot_user_service import HotspotUserService
from app.services.router_service import RouterService
from app.controller.base_controller import BaseController

class HotspotUserController:
    
    @staticmethod
    def list():
        """Listar usuários hotspot"""
        users_result = HotspotUserService.list()
        users = users_result.get("data", [])
        
        routers_result = RouterService.list()
        routers = routers_result.get("data", [])
        
        return {
            "users": users,
            "routers": routers
        }
    
    @staticmethod
    def create():
        """Criar usuário hotspot"""
        data = {
            "router_id": request.form.get("router_id"),
            "username": request.form.get("username"),
            "password": request.form.get("password"),
            "limit_uptime": request.form.get("limit_uptime"),
            "rate_limit": request.form.get("rate_limit")
        }
        
        result = HotspotUserService.create(data)
        
        return BaseController.handle_result(
            result=result,
            success_message="Usuário hotspot criado com sucesso!",
            error_default="Erro ao criar usuário hotspot",
            redirect_to="hotspot_users.list_users"
        )
    
    @staticmethod
    def update(user_id):
        """Atualizar usuário hotspot"""
        data = {
            "username": request.form.get("username"),
            "password": request.form.get("password"),
            "limit_uptime": request.form.get("limit_uptime"),
            "rate_limit": request.form.get("rate_limit")
        }
        
        result = HotspotUserService.update(user_id, data)
        
        return BaseController.handle_result(
            result=result,
            success_message="Usuário hotspot atualizado!",
            error_default="Erro ao atualizar usuário hotspot",
            redirect_to="hotspot_users.list_users"
        )
    
    @staticmethod
    def delete(user_id):
        """Deletar usuário hotspot"""
        result = HotspotUserService.delete(user_id)
        
        return BaseController.handle_result(
            result=result,
            success_message="Usuário removido!",
            error_default="Erro ao remover usuário",
            redirect_to="hotspot_users.list_users"
        )