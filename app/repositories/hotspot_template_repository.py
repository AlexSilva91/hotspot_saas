from app.extensions import db
from app.models.hotspot_template import HotspotTemplate


class HotspotTemplateRepository:


    @staticmethod
    def create(data):

        template = HotspotTemplate(**data)

        db.session.add(template)
        db.session.commit()

        return template


    @staticmethod
    def get_all():

        return HotspotTemplate.query.all()


    @staticmethod
    def get_by_id(template_id):

        return HotspotTemplate.query.get(template_id)


    @staticmethod
    def save(template):

        db.session.add(template)
        db.session.commit()

        return template


    @staticmethod
    def delete(template):

        db.session.delete(template)
        db.session.commit()