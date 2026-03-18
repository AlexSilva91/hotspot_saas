from app.models.bypass_device import BypassDevice
from app.models.router import Router
from app.repositories.base_repository import BaseRepository
from app.middleware.tenant_middleware import tenant_filter

class BypassDeviceRepository(BaseRepository):
    model = BypassDevice

    @classmethod
    def get_all(cls):
        query = cls.model.query.join(Router)
        query = tenant_filter(query)
        return query.all()

    @classmethod
    def get_by_id(cls, device_id):
        query = cls.model.query.join(Router).filter(BypassDevice.id == device_id)
        query = tenant_filter(query)
        return query.first()