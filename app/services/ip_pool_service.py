from app.services.base_service import BaseService
from app.repositories.ip_pool_repository import IpPoolRepository


class IpPoolService(BaseService):
    repository = IpPoolRepository
    not_found_message = "IP Pool não encontrado"