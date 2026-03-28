from flask import Blueprint, render_template
from flask_login import login_required
from app.controller.hotspot_user_controller.hotspot_user_controller import HotspotUserController

hotspot_user_bp = Blueprint("hotspot_users", __name__)

@hotspot_user_bp.route("/hotspot-users", methods=["GET"])
@login_required
def list_users():
    data = HotspotUserController.list()
    return render_template("hotspot_users/list.html", **data)

@hotspot_user_bp.route("/hotspot-users/create", methods=["POST"])
@login_required
def create_user():
    return HotspotUserController.create()

@hotspot_user_bp.route("/hotspot-users/<uuid:user_id>/edit", methods=["POST"])
@login_required
def update_user(user_id):
    return HotspotUserController.update(user_id)

@hotspot_user_bp.route("/hotspot-users/<uuid:user_id>/delete", methods=["POST"])
@login_required
def delete_user(user_id):
    return HotspotUserController.delete(user_id)