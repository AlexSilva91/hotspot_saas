from flask import request, flash, redirect, url_for
from app.services.router_service import RouterService
from app.services.tenant_service import TenantService
from app.controller.base_controller import BaseController

class RouterController:
    
    @staticmethod
    def list():
        """Listar roteadores"""
        result = RouterService.list()
        routers = result.get("data", [])
        
        tenants_result = TenantService.list()
        tenants = tenants_result.get("data", [])
        
        return {
            "routers": routers,
            "tenants": tenants
        }
    
    @staticmethod
    def create():
        """Criar roteador"""
        data = {
            "name": request.form.get("name"),
            "ip_address": request.form.get("ip_address"),
            "api_port": int(request.form.get("api_port") or 8728),
            "username": request.form.get("username"),
            "password": request.form.get("password"),
            "location": request.form.get("location"),
            "tenant_id": request.form.get("tenant_id")
        }
        
        result = RouterService.create(data)
        
        return BaseController.handle_result(
            result=result,
            success_message="Roteador cadastrado com sucesso!",
            error_default="Erro ao cadastrar roteador",
            redirect_to="routers.list_routers"
        )
    
    @staticmethod
    def edit_page(router_id):
        """Página de edição de roteador"""
        result = RouterService.get(router_id)
        
        if not result.get("success"):
            flash(result.get("errors", {}).get("not_found", "Router não encontrado"), "error")
            return redirect(url_for("routers.list_routers"))
        
        router = result["data"]
        
        tenants_result = TenantService.list()
        tenants = tenants_result.get("data", [])
        
        return {
            "router": router,
            "tenants": tenants
        }
    
    @staticmethod
    def update(router_id):
        """Atualizar roteador"""
        data = {
            "name": request.form.get("name"),
            "ip_address": request.form.get("ip_address"),
            "api_port": int(request.form.get("api_port") or 8728),
            "username": request.form.get("username"),
            "password": request.form.get("password"),
            "location": request.form.get("location"),
            "tenant_id": request.form.get("tenant_id")
        }
        
        result = RouterService.update(router_id, data)
        
        return BaseController.handle_result(
            result=result,
            success_message="Roteador atualizado com sucesso!",
            error_default="Erro ao atualizar roteador",
            redirect_to="routers.list_routers"
        )
    
    @staticmethod
    def delete(router_id):
        """Deletar roteador"""
        result = RouterService.delete(router_id)
        
        return BaseController.handle_result(
            result=result,
            success_message="Roteador removido com sucesso!",
            error_default="Erro ao remover roteador",
            redirect_to="routers.list_routers"
        )