from flask import Blueprint, flash, request, render_template, redirect, url_for
from app.services.tenant_service import TenantService
from app.services.plan_service import PlanService
from app.controller.base_controller import BaseController
from flask_login import login_required

tenant_bp = Blueprint("tenants", __name__)


# LISTAR
@tenant_bp.route("/tenants", methods=["GET"])
@login_required
def list_tenants():
    result = TenantService.list()
    tenants = result.get("data", [])
    
    plans_result = PlanService.list()
    plans = plans_result.get("data", [])

    return render_template(
        "tenants/list.html",
        tenants=tenants,
        plans=plans
    )


# CRIAR
@tenant_bp.route("/tenants/create", methods=["POST"])
@login_required
def create_tenant():
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


# PAGINA DE EDIÇÃO
@tenant_bp.route("/tenants/<uuid:tenant_id>/edit", methods=["GET"])
@login_required
def edit_tenant_page(tenant_id):
    result = TenantService.get(tenant_id)
    
    if not result.get("success"):
        flash(result.get("errors", {}).get("not_found", "Empresa não encontrada"), "error")
        return redirect(url_for("tenants.list_tenants"))
    
    tenant = result.get("data")
    
    plans_result = PlanService.list()
    plans = plans_result.get("data", [])

    return render_template(
        "tenants/edit.html",
        tenant=tenant,
        plans=plans
    )


# ATUALIZAR
@tenant_bp.route("/tenants/<uuid:tenant_id>/edit", methods=["POST"])
@login_required
def update_tenant(tenant_id):
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


# REMOVER
@tenant_bp.route("/tenants/<uuid:tenant_id>/delete", methods=["POST"])
@login_required
def delete_tenant(tenant_id):
    result = TenantService.delete(tenant_id)

    return BaseController.handle_result(
        result=result,
        success_message="Empresa deletada com sucesso!",
        error_default="Não foi possível remover empresa!",
        redirect_to="tenants.list_tenants"
    )