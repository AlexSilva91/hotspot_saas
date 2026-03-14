from flask import Blueprint, request, jsonify
from app.services.router_service import RouterService

router_bp = Blueprint("routers", __name__)


@router_bp.route("/routers", methods=["POST"])
def create_router():

    data = request.json

    router = RouterService.create_router(data)

    return jsonify({"id": str(router.id)})


@router_bp.route("/routers", methods=["GET"])
def list_routers():

    routers = RouterService.list_routers()

    result = []

    for router in routers:
        result.append({
            "id": str(router.id),
            "name": router.name,
            "ip": router.ip_address
        })

    return jsonify(result)