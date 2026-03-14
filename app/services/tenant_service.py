from app.repositories.tenant_repository import TenantRepository


class TenantService:

    @staticmethod
    def create_tenant(data):

        return TenantRepository.create(data)


    @staticmethod
    def list_tenants():

        return TenantRepository.get_all()


    @staticmethod
    def get_tenant(tenant_id):

        tenant = TenantRepository.get_by_id(tenant_id)

        if not tenant:
            raise Exception("Tenant não encontrado")

        return tenant


    @staticmethod
    def delete_tenant(tenant_id):

        tenant = TenantRepository.get_by_id(tenant_id)

        if not tenant:
            raise Exception("Tenant não encontrado")

        TenantRepository.delete(tenant)