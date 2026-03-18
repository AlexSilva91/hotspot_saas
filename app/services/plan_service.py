from app.services.base_service import BaseService
from app.repositories.plan_repository import PlanRepository
from sqlalchemy.exc import IntegrityError


class PlanService(BaseService):
    repository = PlanRepository
    not_found_message = "Plano não encontrado"

    @classmethod
    def delete(cls, obj_id):
        obj = cls.repository.get_by_id(obj_id)

        if not obj:
            return {
                "success": False,
                "errors": {"not_found": cls.not_found_message}
            }

        if obj.tenants and len(obj.tenants) > 0:
            tenant_names = [t.name for t in obj.tenants]

            return {
                "success": False,
                "errors": {
                    "general": f"Plano vinculado às empresas: {', '.join(tenant_names)}"
                }
            }

        try:
            cls.repository.delete(obj)
            return {"success": True}

        except IntegrityError:
            return {
                "success": False,
                "errors": {
                    "general": "Existem empresas vinculadas a este plano"
                }
            }