from app.extensions import db
from app.models.plan import Plan


class PlanRepository:


    @staticmethod
    def create(data):

        plan = Plan(**data)

        db.session.add(plan)
        db.session.commit()

        return plan


    @staticmethod
    def get_all():

        return Plan.query.order_by(Plan.created_at.desc()).all()


    @staticmethod
    def get_by_id(plan_id):

        return Plan.query.get(plan_id)


    @staticmethod
    def save(plan):

        db.session.add(plan)
        db.session.commit()

        return plan


    @staticmethod
    def delete(plan):

        db.session.delete(plan)
        db.session.commit()