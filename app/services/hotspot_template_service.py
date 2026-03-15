from app.repositories.hotspot_template_repository import HotspotTemplateRepository


class HotspotTemplateService:


    @staticmethod
    def create_template(data):

        return HotspotTemplateRepository.create(data)


    @staticmethod
    def list_templates():

        return HotspotTemplateRepository.get_all()


    @staticmethod
    def get_template(template_id):

        template = HotspotTemplateRepository.get_by_id(template_id)

        if not template:
            raise Exception("Template não encontrado")

        return template


    @staticmethod
    def update_template(template_id, data):

        template = HotspotTemplateRepository.get_by_id(template_id)

        if not template:
            raise Exception("Template não encontrado")

        for key, value in data.items():
            setattr(template, key, value)

        return HotspotTemplateRepository.save(template)


    @staticmethod
    def delete_template(template_id):

        template = HotspotTemplateRepository.get_by_id(template_id)

        if not template:
            raise Exception("Template não encontrado")

        HotspotTemplateRepository.delete(template)