from app.extensions import db
from app.models.tenant import Tenant


class TenantRepository:

    @staticmethod
    def create(data):

        tenant = Tenant(**data)

        db.session.add(tenant)
        db.session.commit()

        return tenant


    @staticmethod
    def get_all():

        return Tenant.query.all()


    @staticmethod
    def get_by_id(tenant_id):

        return Tenant.query.get(tenant_id)


    @staticmethod
    def delete(tenant):

        db.session.delete(tenant)
        db.session.commit()