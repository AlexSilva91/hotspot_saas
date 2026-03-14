from app.repositories.plan_repository import PlanRepository


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

        PlanRepository.delete(plan)