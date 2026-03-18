from app.models.active_session import ActiveSession
from app.repositories.base_repository import BaseRepository
from app.middleware.tenant_middleware import tenant_filter

class ActiveSessionRepository(BaseRepository):
    model = ActiveSession

    @classmethod
    def get_all(cls):
        query = cls.model.query
        query = tenant_filter(query)
        return query.all()