from app.extensions import db
from app.models.bypass_device import BypassDevice


class BypassDeviceRepository:


    @staticmethod
    def create(data):

        device = BypassDevice(**data)

        db.session.add(device)
        db.session.commit()

        return device


    @staticmethod
    def get_all():

        return BypassDevice.query.all()


    @staticmethod
    def get_by_id(device_id):

        return BypassDevice.query.get(device_id)


    @staticmethod
    def save(device):

        db.session.add(device)
        db.session.commit()

        return device


    @staticmethod
    def delete(device):

        db.session.delete(device)
        db.session.commit()