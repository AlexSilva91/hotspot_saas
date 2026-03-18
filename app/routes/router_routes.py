from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_login import login_required
from app.services.router_service import RouterService
from app.services.tenant_service import TenantService
from app.controller.base_controller import BaseController

router_bp = Blueprint("routers", __name__)


# LISTAR
@router_bp.route("/routers", methods=["GET"])
@login_required
def list_routers():
    result = RouterService.list()
    routers = result.get("data", [])

    tenants_result = TenantService.list()
    tenants = tenants_result.get("data", [])

    return render_template("routers/list.html", routers=routers, tenants=tenants)


# CRIAR
@router_bp.route("/routers/create", methods=["POST"])
@login_required
def create_router():
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


# EDITAR (página)
@router_bp.route("/routers/<uuid:router_id>/edit", methods=["GET"])
@login_required
def edit_router_page(router_id):
    result = RouterService.get(router_id)

    if not result.get("success"):
        flash(result.get("errors", {}).get("not_found", "Router não encontrado"), "error")
        return redirect(url_for("routers.list_routers"))

    router = result["data"]

    tenants_result = TenantService.list()
    tenants = tenants_result.get("data", [])

    return render_template("routers/edit.html", router=router, tenants=tenants)


# ATUALIZAR
@router_bp.route("/routers/<uuid:router_id>/edit", methods=["POST"])
@login_required
def update_router(router_id):
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


# DELETAR
@router_bp.route("/routers/<uuid:router_id>/delete", methods=["POST"])
@login_required
def delete_router(router_id):
    result = RouterService.delete(router_id)

    return BaseController.handle_result(
        result=result,
        success_message="Roteador removido com sucesso!",
        error_default="Erro ao remover roteador",
        redirect_to="routers.list_routers"
    )