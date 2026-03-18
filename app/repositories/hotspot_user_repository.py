from app.models.hotspot_user import HotspotUser
from app.models.router import Router
from app.repositories.base_repository import BaseRepository
from app.middleware.tenant_middleware import tenant_filter

class HotspotUserRepository(BaseRepository):
    model = HotspotUser

    @classmethod
    def get_all(cls):
        query = cls.model.query.join(Router)
        query = tenant_filter(query)
        return query.all()

    @classmethod
    def get_by_id(cls, user_id):
        query = cls.model.query.join(Router).filter(HotspotUser.id == user_id)
        query = tenant_filter(query)
        return query.first()