from app.models.hotspot_template import HotspotTemplate
from app.extensions import db
from app.middleware.tenant_middleware import tenant_filter

class HotspotTemplateRepository:

    @staticmethod
    def create(data):
        template = HotspotTemplate(**data)
        db.session.add(template)
        db.session.commit()
        return template

    @staticmethod
    def get_all():
        query = HotspotTemplate.query
        query = tenant_filter(query)
        return query.all()

    @staticmethod
    def get_by_id(template_id):
        query = HotspotTemplate.query.filter_by(id=template_id)
        query = tenant_filter(query)
        return query.first()

    @staticmethod
    def save(template):
        db.session.add(template)
        db.session.commit()
        return template

    @staticmethod
    def delete(template):
        db.session.delete(template)
        db.session.commit()