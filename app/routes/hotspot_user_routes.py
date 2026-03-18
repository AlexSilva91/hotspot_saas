from flask import Blueprint, request, render_template, redirect, url_for, flash
from app.services.hotspot_user_service import HotspotUserService
from app.services.router_service import RouterService
from app.controller.base_controller import BaseController
from flask_login import login_required

hotspot_user_bp = Blueprint("hotspot_users", __name__)


# LISTAR
@hotspot_user_bp.route("/hotspot-users", methods=["GET"])
@login_required
def list_users():
    users_result = HotspotUserService.list()
    users = users_result.get("data", [])

    routers_result = RouterService.list()
    routers = routers_result.get("data", [])

    return render_template(
        "hotspot_users/list.html",
        users=users,
        routers=routers
    )


# CRIAR
@hotspot_user_bp.route("/hotspot-users/create", methods=["POST"])
@login_required
def create_user():
    data = {
        "router_id": request.form.get("router_id"),
        "username": request.form.get("username"),
        "password": request.form.get("password"),
        "limit_uptime": request.form.get("limit_uptime"),
        "rate_limit": request.form.get("rate_limit")
    }

    result = HotspotUserService.create(data)

    return BaseController.handle_result(
        result=result,
        success_message="Usuário hotspot criado com sucesso!",
        error_default="Erro ao criar usuário hotspot",
        redirect_to="hotspot_users.list_users"
    )


# ATUALIZAR
@hotspot_user_bp.route("/hotspot-users/<uuid:user_id>/edit", methods=["POST"])
@login_required
def update_user(user_id):
    data = {
        "username": request.form.get("username"),
        "password": request.form.get("password"),
        "limit_uptime": request.form.get("limit_uptime"),
        "rate_limit": request.form.get("rate_limit")
    }

    result = HotspotUserService.update(user_id, data)

    return BaseController.handle_result(
        result=result,
        success_message="Usuário hotspot atualizado!",
        error_default="Erro ao atualizar usuário hotspot",
        redirect_to="hotspot_users.list_users"
    )


# DELETAR
@hotspot_user_bp.route("/hotspot-users/<uuid:user_id>/delete", methods=["POST"])
@login_required
def delete_user(user_id):
    result = HotspotUserService.delete(user_id)

    return BaseController.handle_result(
        result=result,
        success_message="Usuário removido!",
        error_default="Erro ao remover usuário",
        redirect_to="hotspot_users.list_users"
    )