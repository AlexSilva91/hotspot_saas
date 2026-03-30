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

    @classmethod
    def get_router(cls, router_id):
        """Busca o roteador vinculado ao device (necessário para credenciais SSH)."""
        return Router.query.get(router_id)

    @classmethod
    def get_by_mac_and_router(cls, mac_address, router_id):
        """Verifica duplicidade de MAC no mesmo roteador."""
        return cls.model.query.filter_by(
            mac_address=mac_address,
            router_id=router_id
        ).first()