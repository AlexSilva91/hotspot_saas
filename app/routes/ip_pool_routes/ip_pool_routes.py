from flask import Blueprint, render_template
from flask_login import login_required
from app.controller.ip_pool_controller.ip_pool_controller import IpPoolController

ip_pool_bp = Blueprint("ip_pools", __name__)

@ip_pool_bp.route("/ip-pools", methods=["GET"])
@login_required
def list_pools():
    data = IpPoolController.list()
    return render_template("ip_pools/list.html", **data)

@ip_pool_bp.route("/ip-pools/create", methods=["POST"])
@login_required
def create_pool():
    return IpPoolController.create()

@ip_pool_bp.route("/ip-pools/<uuid:pool_id>/edit", methods=["POST"])
@login_required
def update_pool(pool_id):
    return IpPoolController.update(pool_id)

@ip_pool_bp.route("/ip-pools/<uuid:pool_id>/delete", methods=["POST"])
@login_required
def delete_pool(pool_id):
    return IpPoolController.delete(pool_id)