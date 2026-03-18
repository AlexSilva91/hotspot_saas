from app.models.tenant import Tenant
from app.repositories.base_repository import BaseRepository
from app.middleware.tenant_middleware import tenant_filter

class TenantRepository(BaseRepository):
    model = Tenant

    @classmethod
    def get_all(cls):
        query = cls.model.query.order_by(Tenant.created_at.desc())
        query = tenant_filter(query)
        return query.all()