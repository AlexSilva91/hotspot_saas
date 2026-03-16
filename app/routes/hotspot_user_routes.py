from flask import Blueprint, request, render_template, redirect, url_for, flash
from app.services.hotspot_user_service import HotspotUserService
from app.services.router_service import RouterService
from flask_login import login_required

hotspot_user_bp = Blueprint("hotspot_users", __name__)


@hotspot_user_bp.route("/hotspot-users", methods=["GET"])
@login_required
def list_users():

    users = HotspotUserService.list_users()
    routers = RouterService.list_routers()
    
    return render_template(
        "hotspot_users/list.html",
        users=users, 
        routers=routers
    )


@hotspot_user_bp.route("/hotspot-users/create", methods=["POST"])
@login_required
def create_user():

    try:

        data = {
            "router_id": request.form.get("router_id"),
            "username": request.form.get("username"),
            "password": request.form.get("password"),
            "limit_uptime": request.form.get("limit_uptime"),
            "rate_limit": request.form.get("rate_limit")
        }

        HotspotUserService.create_user(data)

        flash("Usuário hotspot criado com sucesso!", "success")

    except Exception:

        flash("Erro ao criar usuário hotspot!", "error")

    return redirect(url_for("hotspot_users.list_users"))


@hotspot_user_bp.route("/hotspot-users/<uuid:user_id>/edit", methods=["POST"])
@login_required
def update_user(user_id):

    try:

        data = {
            "username": request.form.get("username"),
            "password": request.form.get("password"),
            "limit_uptime": request.form.get("limit_uptime"),
            "rate_limit": request.form.get("rate_limit")
        }

        HotspotUserService.update_user(user_id, data)

        flash("Usuário hotspot atualizado!", "success")

    except Exception:

        flash("Erro ao atualizar usuário!", "error")

    return redirect(url_for("hotspot_users.list_users"))


@hotspot_user_bp.route("/hotspot-users/<uuid:user_id>/delete", methods=["POST"])
@login_required
def delete_user(user_id):

    try:

        HotspotUserService.delete_user(user_id)

        flash("Usuário removido!", "success")

    except Exception:

        flash("Erro ao remover usuário!", "error")

    return redirect(url_for("hotspot_users.list_users"))