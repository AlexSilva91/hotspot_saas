from flask import Blueprint, flash, request, render_template, redirect, url_for
from app.services.tenant_service import TenantService
from app.services.plan_service import PlanService
from flask_login import login_required

tenant_bp = Blueprint("tenants", __name__)


# LISTAR
@tenant_bp.route("/tenants", methods=["GET"])
@login_required
def list_tenants():

    tenants = TenantService.list_tenants()
    plans = PlanService.list_plans()

    return render_template(
        "tenants/list.html",
        tenants=tenants,
        plans=plans
    )


# CRIAR
@tenant_bp.route("/tenants/create", methods=["POST"])
@login_required
def create_tenant():

    try:

        name = request.form.get("name")
        plan_id = request.form.get("plan_id")
        active = request.form.get("active", "true") == "true"

        data = {
            "name": name,
            "plan_id": plan_id if plan_id else None,
            "active": active
        }

        TenantService.create_tenant(data)

        flash("Empresa cadastrada com sucesso!", "success")

    except Exception as e:

        flash("Não foi possível cadastrar empresa!", "error")

    return redirect(url_for("tenants.list_tenants"))


# PAGINA DE EDIÇÃO
@tenant_bp.route("/tenants/<uuid:tenant_id>/edit", methods=["GET"])
@login_required
def edit_tenant_page(tenant_id):

    tenant = TenantService.get_tenant(tenant_id)
    plans = PlanService.list_plans()

    return render_template(
        "tenants/edit.html",
        tenant=tenant,
        plans=plans
    )


# ATUALIZAR
@tenant_bp.route("/tenants/<uuid:tenant_id>/edit", methods=["POST"])
@login_required
def update_tenant(tenant_id):

    try:

        name = request.form.get("name")
        plan_id = request.form.get("plan_id")
        active = request.form.get("active", "true") == "true"

        data = {
            "name": name,
            "plan_id": plan_id if plan_id else None,
            "active": active
        }

        TenantService.update_tenant(tenant_id, data)

        flash("Empresa atualizada com sucesso!", "success")

    except Exception as e:

        flash("Não foi possível atualizar empresa!", "error")

    return redirect(url_for("tenants.list_tenants"))


# REMOVER
@tenant_bp.route("/tenants/<uuid:tenant_id>/delete", methods=["POST"])
@login_required
def delete_tenant(tenant_id):

    try:

        TenantService.delete_tenant(tenant_id)

        flash("Empresa deletada com sucesso!", "success")

    except Exception as e:

        flash("Não foi possível remover empresa!", "error")

    return redirect(url_for("tenants.list_tenants"))