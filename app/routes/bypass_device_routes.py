from flask import Blueprint, request, render_template, redirect, url_for, flash
from app.services.bypass_device_service import BypassDeviceService
from app.services.router_service import RouterService
from app.decorators.login_required import login_required

bypass_device_bp = Blueprint("bypass_devices", __name__)


@bypass_device_bp.route("/bypass-devices", methods=["GET"])
@login_required
def list_devices():

    devices = BypassDeviceService.list_devices()
    routers = RouterService.list_routers()

    return render_template(
        "bypass_devices/list.html",
        devices=devices, 
        routers=routers
    )


@bypass_device_bp.route("/bypass-devices/create", methods=["POST"])
@login_required
def create_device():

    try:

        data = {
            "router_id": request.form.get("router_id"),
            "mac_address": request.form.get("mac_address"),
            "comment": request.form.get("comment")
        }

        BypassDeviceService.create_device(data)

        flash("Dispositivo adicionado!", "success")

    except Exception:

        flash("Erro ao adicionar dispositivo!", "error")

    return redirect(url_for("bypass_devices.list_devices"))


@bypass_device_bp.route("/bypass-devices/<uuid:device_id>/edit", methods=["POST"])
@login_required
def update_device(device_id):

    try:

        data = {
            "mac_address": request.form.get("mac_address"),
            "comment": request.form.get("comment")
        }

        BypassDeviceService.update_device(device_id, data)

        flash("Dispositivo atualizado!", "success")

    except Exception:

        flash("Erro ao atualizar dispositivo!", "error")

    return redirect(url_for("bypass_devices.list_devices"))


@bypass_device_bp.route("/bypass-devices/<uuid:device_id>/delete", methods=["POST"])
@login_required
def delete_device(device_id):

    try:

        BypassDeviceService.delete_device(device_id)

        flash("Dispositivo removido!", "success")

    except Exception:

        flash("Erro ao remover dispositivo!", "error")

    return redirect(url_for("bypass_devices.list_devices"))