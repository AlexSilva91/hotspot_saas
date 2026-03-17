from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_login import login_required
from app.services.router_service import RouterService
from app.services.tenant_service import TenantService

router_bp = Blueprint("routers", __name__)

# LISTAR
@router_bp.route("/routers", methods=["GET"])
@login_required
def list_routers():
    routers = RouterService.list_routers()
    tenants = TenantService.list_tenants()
    return render_template("routers/list.html", routers=routers, tenants=tenants)

# CRIAR
@router_bp.route("/routers/create", methods=["POST"])
@login_required
def create_router():
    data = {
        "name": request.form.get("name"),
        "ip_address": request.form.get("ip_address"),
        "api_port": request.form.get("api_port") or 8728,
        "username": request.form.get("username"),
        "password": request.form.get("password"),
        "location": request.form.get("location"),
        "tenant_id": request.form.get("tenant_id")
    }

    result = RouterService.create_router(data)

    if result["success"]:
        flash("Roteador cadastrado com sucesso!", "success")
    else:
        for msg in result.get("errors", {}).values():
            flash(msg, "error")

    return redirect(url_for("routers.list_routers"))

# EDITAR (página)
@router_bp.route("/routers/<uuid:router_id>/edit", methods=["GET"])
@login_required
def edit_router_page(router_id):
    router = RouterService.get_router(router_id)
    tenants = TenantService.list_tenants()
    return render_template("routers/edit.html", router=router, tenants=tenants)

# ATUALIZAR
@router_bp.route("/routers/<uuid:router_id>/edit", methods=["POST"])
@login_required
def update_router(router_id):
    data = {
        "name": request.form.get("name"),
        "ip_address": request.form.get("ip_address"),
        "api_port": request.form.get("api_port"),
        "username": request.form.get("username"),
        "password": request.form.get("password"),
        "location": request.form.get("location"),
        "tenant_id": request.form.get("tenant_id")
    }

    result = RouterService.update_router(router_id, data)

    if result["success"]:
        flash("Roteador atualizado com sucesso!", "success")
    else:
        for msg in result.get("errors", {}).values():
            flash(msg, "error")

    return redirect(url_for("routers.list_routers"))

# DELETAR
@router_bp.route("/routers/<uuid:router_id>/delete", methods=["POST"])
@login_required
def delete_router(router_id):
    result = RouterService.delete_router(router_id)

    if result.get("success", False):
        flash("Roteador removido com sucesso!", "success")
    else:
        for msg in result.get("errors", {}).values():
            flash(msg, "error")

    return redirect(url_for("routers.list_routers"))