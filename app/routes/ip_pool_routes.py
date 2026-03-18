from flask import Blueprint, request, redirect, url_for, flash, render_template
from app.services.ip_pool_service import IpPoolService
from app.services.router_service import RouterService
from app.controller.base_controller import BaseController
from flask_login import login_required

ip_pool_bp = Blueprint("ip_pools", __name__)


@ip_pool_bp.route("/ip-pools", methods=["GET"])
@login_required
def list_pools():
    pools_result = IpPoolService.list()
    pools = pools_result.get("data", [])
    
    routers_result = RouterService.list()
    routers = routers_result.get("data", [])

    return render_template(
        "ip_pools/list.html",
        pools=pools,
        routers=routers
    )


@ip_pool_bp.route("/ip-pools/create", methods=["POST"])
@login_required
def create_pool():
    data = {
        "router_id": request.form.get("router_id"),
        "name": request.form.get("name"),
        "range_start": request.form.get("range_start"),
        "range_end": request.form.get("range_end")
    }

    result = IpPoolService.create(data)

    return BaseController.handle_result(
        result=result,
        success_message="IP Pool criado com sucesso",
        error_default="Erro ao criar IP Pool",
        redirect_to="ip_pools.list_pools"
    )


@ip_pool_bp.route("/ip-pools/<uuid:pool_id>/edit", methods=["POST"])
@login_required
def update_pool(pool_id):
    data = {
        "name": request.form.get("name"),
        "range_start": request.form.get("range_start"),
        "range_end": request.form.get("range_end")
    }

    result = IpPoolService.update(pool_id, data)

    return BaseController.handle_result(
        result=result,
        success_message="IP Pool atualizado",
        error_default="Erro ao atualizar",
        redirect_to="ip_pools.list_pools"
    )


@ip_pool_bp.route("/ip-pools/<uuid:pool_id>/delete", methods=["POST"])
@login_required
def delete_pool(pool_id):
    result = IpPoolService.delete(pool_id)

    return BaseController.handle_result(
        result=result,
        success_message="IP Pool removido",
        error_default="Erro ao remover",
        redirect_to="ip_pools.list_pools"
    )