from flask import request
from app.services.bypass_device_service import BypassDeviceService
from app.services.router_service import RouterService
from app.controller.base_controller import BaseController

class BypassDeviceController:
    
    @staticmethod
    def list():
        """Listar dispositivos bypass"""
        devices_result = BypassDeviceService.list()
        devices = devices_result.get("data", [])
        
        routers_result = RouterService.list()
        routers = routers_result.get("data", [])
        
        return {
            "devices": devices,
            "routers": routers
        }
    
    @staticmethod
    def create():
        """Criar dispositivo bypass"""
        data = {
            "router_id": request.form.get("router_id"),
            "mac_address": request.form.get("mac_address"),
            "comment": request.form.get("comment")
        }
        
        result = BypassDeviceService.create(data)
        
        return BaseController.handle_result(
            result=result,
            success_message="Dispositivo adicionado!",
            error_default="Erro ao adicionar dispositivo!",
            redirect_to="bypass_devices.list_devices"
        )
    
    @staticmethod
    def update(device_id):
        """Atualizar dispositivo bypass"""
        data = {
            "mac_address": request.form.get("mac_address"),
            "comment": request.form.get("comment")
        }
        
        result = BypassDeviceService.update(device_id, data)
        
        return BaseController.handle_result(
            result=result,
            success_message="Dispositivo atualizado!",
            error_default="Erro ao atualizar dispositivo!",
            redirect_to="bypass_devices.list_devices"
        )
    
    @staticmethod
    def delete(device_id):
        """Deletar dispositivo bypass"""
        result = BypassDeviceService.delete(device_id)
        
        return BaseController.handle_result(
            result=result,
            success_message="Dispositivo removido!",
            error_default="Erro ao remover dispositivo!",
            redirect_to="bypass_devices.list_devices"
        )