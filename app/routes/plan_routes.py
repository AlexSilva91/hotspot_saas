from flask import Blueprint, flash, request, render_template, redirect, url_for
from app.services.plan_service import PlanService
from flask_login import login_required

plan_bp = Blueprint("plans", __name__)


# LISTAR PLANOS
@plan_bp.route("/plans", methods=["GET"])
@login_required
def list_plans():

    plans = PlanService.list_plans()

    return render_template(
        "plans/list.html",
        plans=plans
    )


# CRIAR PLANO
@plan_bp.route("/plans/create", methods=["POST"])
@login_required
def create_plan():

    try:

        data = {
            "name": request.form["name"],
            "max_routers": request.form["max_routers"],
            "max_users": request.form["max_users"],
            "max_hotspot_users": request.form["max_hotspot_users"],
        }

        PlanService.create_plan(data)

        flash("Plano cadastrado com sucesso!", "success")

    except Exception:
        flash("Não foi possível cadastrar plano!", "error")

    return redirect(url_for("plans.list_plans"))


# PAGINA DE EDIÇÃO
@plan_bp.route("/plans/<uuid:plan_id>/edit", methods=["GET"])
@login_required
def edit_plan_page(plan_id):

    plan = PlanService.get_plan(plan_id)

    return render_template(
        "plans/edit.html",
        plan=plan
    )


# ATUALIZAR
@plan_bp.route("/plans/<uuid:plan_id>/edit", methods=["POST"])
@login_required
def update_plan(plan_id):

    try:

        data = {
            "name": request.form["name"],
            "max_routers": request.form["max_routers"],
            "max_users": request.form["max_users"],
            "max_hotspot_users": request.form["max_hotspot_users"],
        }

        PlanService.update_plan(plan_id, data)

        flash("Plano atualizado com sucesso!", "success")

    except Exception:
        flash("Não foi possível atualizar plano!", "error")

    return redirect(url_for("plans.list_plans"))


# REMOVER
@plan_bp.route("/plans/<uuid:plan_id>/delete", methods=["POST"])
@login_required
def delete_plan(plan_id):

    try:

        PlanService.delete_plan(plan_id)

        flash("Plano removido com sucesso!", "success")

    except Exception as e:

        flash(str(e), "error")

    return redirect(url_for("plans.list_plans"))