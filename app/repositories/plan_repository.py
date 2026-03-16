from app.extensions import db
from app.models.plan import Plan
from app.middleware.tenant_middleware import tenant_filter

class PlanRepository:

    @staticmethod
    def create(data):
        plan = Plan(**data)
        db.session.add(plan)
        db.session.commit()
        return plan

    @staticmethod
    def get_all():
        query = Plan.query.order_by(Plan.created_at.desc())
        query = tenant_filter(query)  # Aplica filtro por tenant
        return query.all()

    @staticmethod
    def get_by_id(plan_id):
        query = Plan.query.filter_by(id=plan_id)
        query = tenant_filter(query)  # Aplica filtro por tenant
        return query.first()

    @staticmethod
    def save(plan):
        db.session.add(plan)
        db.session.commit()
        return plan

    @staticmethod
    def delete(plan):
        db.session.delete(plan)
        db.session.commit()