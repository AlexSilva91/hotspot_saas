from flask import request
from app.services.ip_pool_service import IpPoolService
from app.services.router_service import RouterService
from app.controller.base_controller import BaseController

class IpPoolController:
    
    @staticmethod
    def list():
        """Listar IP Pools"""
        pools_result = IpPoolService.list()
        pools = pools_result.get("data", [])
        
        routers_result = RouterService.list()
        routers = routers_result.get("data", [])
        
        return {
            "pools": pools,
            "routers": routers
        }
    
    @staticmethod
    def create():
        """Criar IP Pool"""
        data = {
            "router_id": request.form.get("router_id"),
            "name": request.form.get("name"),
            "range_start": request.form.get("range_start"),
            "range_end": request.form.get("range_end")
        }
        
        result = IpPoolService.create(data)
        
        return BaseController.handle_result(
            result=result,
            success_message="IP Pool criado com sucesso",
            error_default="Erro ao criar IP Pool",
            redirect_to="ip_pools.list_pools"
        )
    
    @staticmethod
    def update(pool_id):
        """Atualizar IP Pool"""
        data = {
            "name": request.form.get("name"),
            "range_start": request.form.get("range_start"),
            "range_end": request.form.get("range_end")
        }
        
        result = IpPoolService.update(pool_id, data)
        
        return BaseController.handle_result(
            result=result,
            success_message="IP Pool atualizado",
            error_default="Erro ao atualizar",
            redirect_to="ip_pools.list_pools"
        )
    
    @staticmethod
    def delete(pool_id):
        """Deletar IP Pool"""
        result = IpPoolService.delete(pool_id)
        
        return BaseController.handle_result(
            result=result,
            success_message="IP Pool removido",
            error_default="Erro ao remover",
            redirect_to="ip_pools.list_pools"
        )