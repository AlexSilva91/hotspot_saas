from flask import Blueprint, request, render_template, redirect, url_for, flash
from app.services.hotspot_template_service import HotspotTemplateService
from app.services.tenant_service import TenantService
from app.controller.base_controller import BaseController
from flask_login import login_required

hotspot_template_bp = Blueprint("hotspot_templates", __name__)


@hotspot_template_bp.route("/hotspot-templates", methods=["GET"])
@login_required
def list_templates():
    templates_result = HotspotTemplateService.list()
    templates = templates_result.get("data", [])
    
    tenants_result = TenantService.list()
    tenants = tenants_result.get("data", [])

    return render_template(
        "hotspot_templates/list.html",
        templates=templates,
        tenants=tenants
    )


@hotspot_template_bp.route("/hotspot-templates/create", methods=["POST"])
@login_required
def create_template():
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


@hotspot_template_bp.route("/hotspot-templates/<uuid:template_id>/edit", methods=["POST"])
@login_required
def update_template(template_id):
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


@hotspot_template_bp.route("/hotspot-templates/<uuid:template_id>/delete", methods=["POST"])
@login_required
def delete_template(template_id):
    result = HotspotTemplateService.delete(template_id)

    return BaseController.handle_result(
        result=result,
        success_message="Template removido!",
        error_default="Erro ao remover template!",
        redirect_to="hotspot_templates.list_templates"
    )