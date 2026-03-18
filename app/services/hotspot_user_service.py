from app.services.base_service import BaseService
from app.repositories.hotspot_user_repository import HotspotUserRepository
from app.decorators.plan_limit import enforce_plan_limits


class HotspotUserService(BaseService):
    repository = HotspotUserRepository
    not_found_message = "Usuário hotspot não encontrado"

    allowed_update_fields = [
        "username",
        "password",
        "limit_uptime",
        "rate_limit",
        "router_id"
    ]

    @classmethod
    @enforce_plan_limits(resource="hotspot_user")
    def create(cls, data):
        return super().create(data)

    @classmethod
    def update(cls, obj_id, data):
        return super().update(obj_id, data)