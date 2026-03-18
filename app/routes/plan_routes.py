from flask import Blueprint, flash, request, render_template, redirect, url_for
from app.services.plan_service import PlanService
from app.controller.base_controller import BaseController
from flask_login import login_required

plan_bp = Blueprint("plans", __name__)


# LISTAR PLANOS
@plan_bp.route("/plans", methods=["GET"])
@login_required
def list_plans():
    result = PlanService.list()
    plans = result.get("data", [])

    return render_template(
        "plans/list.html",
        plans=plans
    )


# CRIAR PLANO
@plan_bp.route("/plans/create", methods=["POST"])
@login_required
def create_plan():
    data = {
        "name": request.form.get("name"),
        "max_routers": request.form.get("max_routers"),
        "max_users": request.form.get("max_users"),
        "max_hotspot_users": request.form.get("max_hotspot_users"),
    }

    result = PlanService.create(data)

    return BaseController.handle_result(
        result=result,
        success_message="Plano cadastrado com sucesso!",
        error_default="Não foi possível cadastrar plano!",
        redirect_to="plans.list_plans"
    )


# PAGINA DE EDIÇÃO
@plan_bp.route("/plans/<uuid:plan_id>/edit", methods=["GET"])
@login_required
def edit_plan_page(plan_id):
    result = PlanService.get(plan_id)
    
    if not result.get("success"):
        flash(result.get("errors", {}).get("not_found", "Plano não encontrado"), "error")
        return redirect(url_for("plans.list_plans"))
    
    plan = result.get("data")

    return render_template(
        "plans/edit.html",
        plan=plan
    )


# ATUALIZAR
@plan_bp.route("/plans/<uuid:plan_id>/edit", methods=["POST"])
@login_required
def update_plan(plan_id):
    data = {
        "name": request.form.get("name"),
        "max_routers": request.form.get("max_routers"),
        "max_users": request.form.get("max_users"),
        "max_hotspot_users": request.form.get("max_hotspot_users"),
    }

    result = PlanService.update(plan_id, data)

    return BaseController.handle_result(
        result=result,
        success_message="Plano atualizado com sucesso!",
        error_default="Não foi possível atualizar plano!",
        redirect_to="plans.list_plans"
    )


# REMOVER
@plan_bp.route("/plans/<uuid:plan_id>/delete", methods=["POST"])
@login_required
def delete_plan(plan_id):
    result = PlanService.delete(plan_id)

    return BaseController.handle_result(
        result=result,
        success_message="Plano removido com sucesso!",
        error_default="Erro ao remover plano!",
        redirect_to="plans.list_plans"
    )