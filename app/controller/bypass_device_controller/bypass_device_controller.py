from flask import request
from app.services.bypass_device_service import BypassDeviceService
from app.services.router_service import RouterService
from app.controller.base_controller import BaseController


class BypassDeviceController:

    @staticmethod
    def list():
        devices_result = BypassDeviceService.list()
        routers_result = RouterService.list()
        return {
            "devices": devices_result.get("data", []),
            "routers": routers_result.get("data", []),
        }

    @staticmethod
    def create():
        data = {
            "router_id":   request.form.get("router_id"),
            "mac_address": request.form.get("mac_address"),
            "comment":     request.form.get("comment"),
        }
        result = BypassDeviceService.create(data)
        return BaseController.handle_result(
            result=result,
            success_message="Dispositivo adicionado!",
            error_default="Erro ao adicionar dispositivo!",
            redirect_to="bypass_devices.list_devices",
        )

    @staticmethod
    def update(device_id):
        data = {
            "mac_address":  request.form.get("mac_address"),
            "comment":      request.form.get("comment"),
            "binding_type": request.form.get("binding_type"),
            "active":       request.form.get("active") == "1",
        }
        result = BypassDeviceService.update(device_id, data)
        return BaseController.handle_result(
            result=result,
            success_message="Dispositivo atualizado!",
            error_default="Erro ao atualizar dispositivo!",
            redirect_to="bypass_devices.list_devices",
        )

    @staticmethod
    def delete(device_id):
        result = BypassDeviceService.delete(device_id)
        return BaseController.handle_result(
            result=result,
            success_message="Dispositivo desativado!",
            error_default="Erro ao desativar dispositivo!",
            redirect_to="bypass_devices.list_devices",
        )

    @staticmethod
    def enable(device_id):
        result = BypassDeviceService.enable(device_id)
        return BaseController.handle_result(
            result=result,
            success_message="Dispositivo reativado!",
            error_default="Erro ao reativar dispositivo!",
            redirect_to="bypass_devices.list_devices",
        )

    @staticmethod
    def change_type(device_id):
        new_type = request.form.get("binding_type")  # blocked | bypassed | regular
        result = BypassDeviceService.change_type(device_id, new_type)
        return BaseController.handle_result(
            result=result,
            success_message="Tipo atualizado!",
            error_default="Erro ao atualizar tipo!",
            redirect_to="bypass_devices.list_devices",
        )