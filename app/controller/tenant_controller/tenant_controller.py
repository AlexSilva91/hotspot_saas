from flask import request, flash, redirect, url_for
from app.services.tenant_service import TenantService
from app.services.plan_service import PlanService
from app.controller.base_controller import BaseController

class TenantController:
    
    @staticmethod
    def list():
        """Listar tenants"""
        result = TenantService.list()
        tenants = result.get("data", [])
        
        plans_result = PlanService.list()
        plans = plans_result.get("data", [])
        
        return {
            "tenants": tenants,
            "plans": plans
        }
    
    @staticmethod
    def create():
        """Criar tenant"""
        name = request.form.get("name")
        plan_id = request.form.get("plan_id")
        active = request.form.get("active", "true") == "true"
        
        data = {
            "name": name,
            "plan_id": plan_id if plan_id else None,
            "active": active
        }
        
        result = TenantService.create(data)
        
        return BaseController.handle_result(
            result=result,
            success_message="Empresa cadastrada com sucesso!",
            error_default="Não foi possível cadastrar empresa!",
            redirect_to="tenants.list_tenants"
        )
    
    @staticmethod
    def edit_page(tenant_id):
        """Página de edição de tenant"""
        result = TenantService.get(tenant_id)
        
        if not result.get("success"):
            flash(result.get("errors", {}).get("not_found", "Empresa não encontrada"), "error")
            return redirect(url_for("tenants.list_tenants"))
        
        tenant = result.get("data")
        
        plans_result = PlanService.list()
        plans = plans_result.get("data", [])
        
        return {
            "tenant": tenant,
            "plans": plans
        }
    
    @staticmethod
    def update(tenant_id):
        """Atualizar tenant"""
        name = request.form.get("name")
        plan_id = request.form.get("plan_id")
        active = request.form.get("active", "true") == "true"
        
        data = {
            "name": name,
            "plan_id": plan_id if plan_id else None,
            "active": active
        }
        
        result = TenantService.update(tenant_id, data)
        
        return BaseController.handle_result(
            result=result,
            success_message="Empresa atualizada com sucesso!",
            error_default="Não foi possível atualizar empresa!",
            redirect_to="tenants.list_tenants"
        )
    
    @staticmethod
    def delete(tenant_id):
        """Deletar tenant"""
        result = TenantService.delete(tenant_id)
        
        return BaseController.handle_result(
            result=result,
            success_message="Empresa deletada com sucesso!",
            error_default="Não foi possível remover empresa!",
            redirect_to="tenants.list_tenants"
        )