from app.services.base_service import BaseService
from app.repositories.hotspot_template_repository import HotspotTemplateRepository


class HotspotTemplateService(BaseService):
    repository = HotspotTemplateRepository
    not_found_message = "Template não encontrado"