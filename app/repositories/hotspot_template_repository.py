from app.models.hotspot_template import HotspotTemplate
from app.repositories.base_repository import BaseRepository
from app.middleware.tenant_middleware import tenant_filter

class HotspotTemplateRepository(BaseRepository):
    model = HotspotTemplate

    @classmethod
    def get_all(cls):
        query = cls.model.query
        query = tenant_filter(query)
        return query.all()