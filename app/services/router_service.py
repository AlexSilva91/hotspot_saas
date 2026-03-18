from app.services.base_service import BaseService
from app.repositories.router_repository import RouterRepository
from app.decorators.plan_limit import enforce_plan_limits


class RouterService(BaseService):
    repository = RouterRepository
    not_found_message = "Router não encontrado"

    @classmethod
    @enforce_plan_limits(resource="router")
    def create(cls, data):
        return super().create(data)

    @classmethod
    def update(cls, obj_id, data):
        return super().update(obj_id, data)