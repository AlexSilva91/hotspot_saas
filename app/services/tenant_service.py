from app.services.base_service import BaseService
from app.repositories.tenant_repository import TenantRepository


class TenantService(BaseService):
    repository = TenantRepository
    not_found_message = "Tenant não encontrado"