from flask import request, flash, redirect, url_for
from app.services.plan_service import PlanService
from app.controller.base_controller import BaseController

class PlanController:
    
    @staticmethod
    def list():
        """Listar planos"""
        result = PlanService.list()
        plans = result.get("data", [])
        
        return {"plans": plans}
    
    @staticmethod
    def create():
        """Criar plano"""
        data = {
            "name": request.form.get("name"),
            "max_routers": request.form.get("max_routers"),
            "max_users": request.form.get("max_users"),
            "max_hotspot_users": request.form.get("max_hotspot_users"),
        }
        
        result = PlanService.create(data)
        
        return BaseController.handle_result(
            result=result,
            success_message="Plano cadastrado com sucesso!",
            error_default="Não foi possível cadastrar plano!",
            redirect_to="plans.list_plans"
        )
    
    @staticmethod
    def edit_page(plan_id):
        """Página de edição de plano"""
        result = PlanService.get(plan_id)
        
        if not result.get("success"):
            flash(result.get("errors", {}).get("not_found", "Plano não encontrado"), "error")
            return redirect(url_for("plans.list_plans"))
        
        plan = result.get("data")
        
        return {"plan": plan}
    
    @staticmethod
    def update(plan_id):
        """Atualizar plano"""
        data = {
            "name": request.form.get("name"),
            "max_routers": request.form.get("max_routers"),
            "max_users": request.form.get("max_users"),
            "max_hotspot_users": request.form.get("max_hotspot_users"),
        }
        
        result = PlanService.update(plan_id, data)
        
        return BaseController.handle_result(
            result=result,
            success_message="Plano atualizado com sucesso!",
            error_default="Não foi possível atualizar plano!",
            redirect_to="plans.list_plans"
        )
    
    @staticmethod
    def delete(plan_id):
        """Deletar plano"""
        result = PlanService.delete(plan_id)
        
        return BaseController.handle_result(
            result=result,
            success_message="Plano removido com sucesso!",
            error_default="Erro ao remover plano!",
            redirect_to="plans.list_plans"
        )