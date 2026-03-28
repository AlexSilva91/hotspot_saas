from flask import Blueprint, render_template
from flask_login import login_required
from app.controller.plan_controller.plan_controller import PlanController

plan_bp = Blueprint("plans", __name__)

@plan_bp.route("/plans", methods=["GET"])
@login_required
def list_plans():
    data = PlanController.list()
    return render_template("plans/list.html", **data)

@plan_bp.route("/plans/create", methods=["POST"])
@login_required
def create_plan():
    return PlanController.create()

@plan_bp.route("/plans/<uuid:plan_id>/edit", methods=["GET"])
@login_required
def edit_plan_page(plan_id):
    data = PlanController.edit_page(plan_id)
    if isinstance(data, dict):
        return render_template("plans/edit.html", **data)
    return data

@plan_bp.route("/plans/<uuid:plan_id>/edit", methods=["POST"])
@login_required
def update_plan(plan_id):
    return PlanController.update(plan_id)

@plan_bp.route("/plans/<uuid:plan_id>/delete", methods=["POST"])
@login_required
def delete_plan(plan_id):
    return PlanController.delete(plan_id)