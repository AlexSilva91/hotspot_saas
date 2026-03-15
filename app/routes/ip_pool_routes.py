from flask import Blueprint, request, redirect, url_for, flash, render_template
from app.services.ip_pool_service import IpPoolService
from app.services.router_service import RouterService
from app.decorators.login_required import login_required

ip_pool_bp = Blueprint("ip_pools", __name__)


@ip_pool_bp.route("/ip-pools")
@login_required
def list_pools():

    pools = IpPoolService.list_pools()
    routers = RouterService.list_routers()

    return render_template(
        "ip_pools/list.html",
        pools=pools,
        routers=routers
    )


@ip_pool_bp.route("/ip-pools/create", methods=["POST"])
@login_required
def create_pool():

    try:

        data = {
            "router_id": request.form.get("router_id"),
            "name": request.form.get("name"),
            "range_start": request.form.get("range_start"),
            "range_end": request.form.get("range_end")
        }

        IpPoolService.create_pool(data)

        flash("IP Pool criado com sucesso", "success")

    except Exception:

        flash("Erro ao criar IP Pool", "error")

    return redirect(url_for("ip_pools.list_pools"))


@ip_pool_bp.route("/ip-pools/<uuid:pool_id>/edit", methods=["POST"])
@login_required
def update_pool(pool_id):

    try:

        data = {
            "name": request.form.get("name"),
            "range_start": request.form.get("range_start"),
            "range_end": request.form.get("range_end")
        }

        IpPoolService.update_pool(pool_id, data)

        flash("IP Pool atualizado", "success")

    except Exception:

        flash("Erro ao atualizar", "error")

    return redirect(url_for("ip_pools.list_pools"))


@ip_pool_bp.route("/ip-pools/<uuid:pool_id>/delete", methods=["POST"])
@login_required
def delete_pool(pool_id):

    try:

        IpPoolService.delete_pool(pool_id)

        flash("IP Pool removido", "success")

    except Exception:

        flash("Erro ao remover", "error")

    return redirect(url_for("ip_pools.list_pools"))