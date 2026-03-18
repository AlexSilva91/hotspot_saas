from app.models.ip_pool import IpPool
from app.models.router import Router
from app.repositories.base_repository import BaseRepository
from app.middleware.tenant_middleware import tenant_filter

class IpPoolRepository(BaseRepository):
    model = IpPool

    @classmethod
    def get_all(cls):
        query = cls.model.query.join(Router)
        query = tenant_filter(query)
        return query.all()

    @classmethod
    def get_by_id(cls, pool_id):
        query = cls.model.query.join(Router).filter(IpPool.id == pool_id)
        query = tenant_filter(query)
        return query.first()