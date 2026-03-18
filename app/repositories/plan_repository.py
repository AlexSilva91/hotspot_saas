from app.models.plan import Plan
from app.repositories.base_repository import BaseRepository
from app.middleware.tenant_middleware import tenant_filter

class PlanRepository(BaseRepository):
    model = Plan

    @classmethod
    def get_all(cls):
        query = cls.model.query.order_by(Plan.created_at.desc())
        query = tenant_filter(query)
        return query.all()