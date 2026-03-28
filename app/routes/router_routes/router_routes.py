from flask import Blueprint, render_template
from flask_login import login_required
from app.controller.router_controller.router_controller import RouterController

router_bp = Blueprint("routers", __name__)

@router_bp.route("/routers", methods=["GET"])
@login_required
def list_routers():
    data = RouterController.list()
    return render_template("routers/list.html", **data)

@router_bp.route("/routers/create", methods=["POST"])
@login_required
def create_router():
    return RouterController.create()

@router_bp.route("/routers/<uuid:router_id>/edit", methods=["GET"])
@login_required
def edit_router_page(router_id):
    data = RouterController.edit_page(router_id)
    if isinstance(data, dict):
        return render_template("routers/edit.html", **data)
    return data

@router_bp.route("/routers/<uuid:router_id>/edit", methods=["POST"])
@login_required
def update_router(router_id):
    return RouterController.update(router_id)

@router_bp.route("/routers/<uuid:router_id>/delete", methods=["POST"])
@login_required
def delete_router(router_id):
    return RouterController.delete(router_id)