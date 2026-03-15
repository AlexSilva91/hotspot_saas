from app.repositories.plan_repository import PlanRepository
from sqlalchemy.exc import IntegrityError
from flask import flash

class PlanService:

    @staticmethod
    def create_plan(data):
        return PlanRepository.create(data)

    @staticmethod
    def list_plans():
        return PlanRepository.get_all()

    @staticmethod
    def get_plan(plan_id):
        plan = PlanRepository.get_by_id(plan_id)
        if not plan:
            raise Exception("Plano não encontrado")
        return plan

    @staticmethod
    def delete_plan(plan_id):
        plan = PlanRepository.get_by_id(plan_id)

        if not plan:
            raise Exception("Plano não encontrado")

        if plan.tenants and len(plan.tenants) > 0:
            tenant_names = [tenant.name for tenant in plan.tenants]
            raise Exception(f"Não é possível excluir este plano pois está vinculado às seguintes empresas: {', '.join(tenant_names)}")

        try:
            PlanRepository.delete(plan)
        except IntegrityError:
            raise Exception("Não é possível excluir este plano pois existem empresas vinculadas a ele")