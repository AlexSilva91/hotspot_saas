from flask import Blueprint, request, render_template, redirect, url_for
from app.services.tenant_service import TenantService
from app.services.plan_service import PlanService

tenant_bp = Blueprint("tenants", __name__)


# LISTAR
@tenant_bp.route("/tenants", methods=["GET"])
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
def create_tenant():

    plan_id = request.form.get("plan_id")

    data = {
        "name": request.form.get("name"),
        "plan_id": plan_id if plan_id else None
    }

    TenantService.create_tenant(data)

    return redirect(url_for("tenants.list_tenants"))


# PAGINA DE EDIÇÃO
@tenant_bp.route("/tenants/<uuid:tenant_id>/edit", methods=["GET"])
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
def update_tenant(tenant_id):

    tenant = TenantService.get_tenant(tenant_id)

    tenant.name = request.form.get("name")

    plan_id = request.form.get("plan_id")
    tenant.plan_id = plan_id if plan_id else None

    from app.extensions import db
    db.session.commit()

    return redirect(url_for("tenants.list_tenants"))


# REMOVER
@tenant_bp.route("/tenants/<uuid:tenant_id>/delete", methods=["POST"])
def delete_tenant(tenant_id):

    TenantService.delete_tenant(tenant_id)

    return redirect(url_for("tenants.list_tenants"))