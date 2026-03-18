from flask import Blueprint, request, render_template, redirect, url_for, flash
from app.services.bypass_device_service import BypassDeviceService
from app.services.router_service import RouterService
from app.controller.base_controller import BaseController
from flask_login import login_required

bypass_device_bp = Blueprint("bypass_devices", __name__)


@bypass_device_bp.route("/bypass-devices", methods=["GET"])
@login_required
def list_devices():
    devices_result = BypassDeviceService.list()
    devices = devices_result.get("data", [])
    
    routers_result = RouterService.list()
    routers = routers_result.get("data", [])

    return render_template(
        "bypass_devices/list.html",
        devices=devices, 
        routers=routers
    )


@bypass_device_bp.route("/bypass-devices/create", methods=["POST"])
@login_required
def create_device():
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


@bypass_device_bp.route("/bypass-devices/<uuid:device_id>/edit", methods=["POST"])
@login_required
def update_device(device_id):
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


@bypass_device_bp.route("/bypass-devices/<uuid:device_id>/delete", methods=["POST"])
@login_required
def delete_device(device_id):
    result = BypassDeviceService.delete(device_id)

    return BaseController.handle_result(
        result=result,
        success_message="Dispositivo removido!",
        error_default="Erro ao remover dispositivo!",
        redirect_to="bypass_devices.list_devices"
    )