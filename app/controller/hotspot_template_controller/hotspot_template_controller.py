from flask import request
from app.services.hotspot_template_service import HotspotTemplateService
from app.services.tenant_service import TenantService
from app.controller.base_controller import BaseController

class HotspotTemplateController:
    
    @staticmethod
    def list():
        """Listar templates hotspot"""
        templates_result = HotspotTemplateService.list()
        templates = templates_result.get("data", [])
        
        tenants_result = TenantService.list()
        tenants = tenants_result.get("data", [])
        
        return {
            "templates": templates,
            "tenants": tenants
        }
    
    @staticmethod
    def create():
        """Criar template hotspot"""
        data = {
            "tenant_id": request.form.get("tenant_id"),
            "name": request.form.get("name"),
            "login_html": request.form.get("login_html"),
            "status_html": request.form.get("status_html"),
            "logo_url": request.form.get("logo_url")
        }
        
        result = HotspotTemplateService.create(data)
        
        return BaseController.handle_result(
            result=result,
            success_message="Template criado com sucesso!",
            error_default="Erro ao criar template!",
            redirect_to="hotspot_templates.list_templates"
        )
    
    @staticmethod
    def update(template_id):
        """Atualizar template hotspot"""
        data = {
            "name": request.form.get("name"),
            "login_html": request.form.get("login_html"),
            "status_html": request.form.get("status_html"),
            "logo_url": request.form.get("logo_url")
        }
        
        result = HotspotTemplateService.update(template_id, data)
        
        return BaseController.handle_result(
            result=result,
            success_message="Template atualizado!",
            error_default="Erro ao atualizar template!",
            redirect_to="hotspot_templates.list_templates"
        )
    
    @staticmethod
    def delete(template_id):
        """Deletar template hotspot"""
        result = HotspotTemplateService.delete(template_id)
        
        return BaseController.handle_result(
            result=result,
            success_message="Template removido!",
            error_default="Erro ao remover template!",
            redirect_to="hotspot_templates.list_templates"
        )