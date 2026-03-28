from flask import Blueprint, render_template
from flask_login import login_required
from app.controller.tenant_controller.tenant_controller import TenantController

tenant_bp = Blueprint("tenants", __name__)

@tenant_bp.route("/tenants", methods=["GET"])
@login_required
def list_tenants():
    data = TenantController.list()
    return render_template("tenants/list.html", **data)

@tenant_bp.route("/tenants/create", methods=["POST"])
@login_required
def create_tenant():
    return TenantController.create()

@tenant_bp.route("/tenants/<uuid:tenant_id>/edit", methods=["GET"])
@login_required
def edit_tenant_page(tenant_id):
    data = TenantController.edit_page(tenant_id)
    if isinstance(data, dict):
        return render_template("tenants/edit.html", **data)
    return data

@tenant_bp.route("/tenants/<uuid:tenant_id>/edit", methods=["POST"])
@login_required
def update_tenant(tenant_id):
    return TenantController.update(tenant_id)

@tenant_bp.route("/tenants/<uuid:tenant_id>/delete", methods=["POST"])
@login_required
def delete_tenant(tenant_id):
    return TenantController.delete(tenant_id)