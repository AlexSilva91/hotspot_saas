from flask import Blueprint, request, jsonify
from app.services.plan_service import PlanService

plan_bp = Blueprint("plans", __name__)


@plan_bp.route("/plans", methods=["POST"])
def create_plan():

    data = request.json

    plan = PlanService.create_plan(data)

    return jsonify({"id": str(plan.id)})


@plan_bp.route("/plans", methods=["GET"])
def list_plans():

    plans = PlanService.list_plans()

    result = []

    for plan in plans:
        result.append({
            "id": str(plan.id),
            "name": plan.name,
            "max_routers": plan.max_routers,
            "max_users": plan.max_users
        })

    return jsonify(result)