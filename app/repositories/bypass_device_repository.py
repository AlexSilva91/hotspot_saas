from app.models.bypass_device import BypassDevice
from app.models.router import Router
from app.extensions import db
from app.middleware.tenant_middleware import tenant_filter

class BypassDeviceRepository:

    @staticmethod
    def create(data):
        device = BypassDevice(**data)
        db.session.add(device)
        db.session.commit()
        return device

    @staticmethod
    def get_all():
        query = BypassDevice.query.join(Router)
        query = tenant_filter(query)
        return query.all()

    @staticmethod
    def get_by_id(device_id):
        query = BypassDevice.query.join(Router).filter(BypassDevice.id == device_id)
        query = tenant_filter(query)
        return query.first()

    @staticmethod
    def save(device):
        db.session.add(device)
        db.session.commit()
        return device

    @staticmethod
    def delete(device):
        db.session.delete(device)
        db.session.commit()