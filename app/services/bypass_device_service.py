from app.services.base_service import BaseService
from app.repositories.bypass_device_repository import BypassDeviceRepository


class BypassDeviceService(BaseService):
    repository = BypassDeviceRepository
    not_found_message = "Dispositivo não encontrado"