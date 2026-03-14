from flask import Blueprint, request, render_template, redirect, url_for
from app.services.plan_service import PlanService

plan_bp = Blueprint("plans", __name__)


# LISTAR PLANOS
@plan_bp.route("/plans", methods=["GET"])
def list_plans():

    plans = PlanService.list_plans()

    return render_template(
        "plans/list.html",
        plans=plans
    )


# CRIAR PLANO
@plan_bp.route("/plans/create", methods=["POST"])
def create_plan():

    data = {
        "name": request.form.get("name"),
        "max_routers": request.form.get("max_routers"),
        "max_users": request.form.get("max_users")
    }

    PlanService.create_plan(data)

    return redirect(url_for("plans.list_plans"))


# PAGINA DE EDIÇÃO
@plan_bp.route("/plans/<uuid:plan_id>/edit", methods=["GET"])
def edit_plan_page(plan_id):

    plan = PlanService.get_plan(plan_id)

    return render_template(
        "plans/edit.html",
        plan=plan
    )


# ATUALIZAR
@plan_bp.route("/plans/<uuid:plan_id>/edit", methods=["POST"])
def update_plan(plan_id):

    plan = PlanService.get_plan(plan_id)

    plan.name = request.form.get("name")
    plan.max_routers = request.form.get("max_routers")
    plan.max_users = request.form.get("max_users")

    from app.extensions import db
    db.session.commit()

    return redirect(url_for("plans.list_plans"))


# REMOVER
@plan_bp.route("/plans/<uuid:plan_id>/delete", methods=["POST"])
def delete_plan(plan_id):

    PlanService.delete_plan(plan_id)

    return redirect(url_for("plans.list_plans"))