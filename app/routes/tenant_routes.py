from flask import Blueprint, request, jsonify
from app.services.tenant_service import TenantService

tenant_bp = Blueprint("tenants", __name__)


@tenant_bp.route("/tenants", methods=["POST"])
def create_tenant():

    data = request.json

    tenant = TenantService.create_tenant(data)

    return jsonify({
        "id": str(tenant.id),
        "name": tenant.name
    })


@tenant_bp.route("/tenants", methods=["GET"])
def list_tenants():

    tenants = TenantService.list_tenants()

    result = []

    for tenant in tenants:

        result.append({
            "id": str(tenant.id),
            "name": tenant.name,
            "plan_id": str(tenant.plan_id) if tenant.plan_id else None
        })

    return jsonify(result)