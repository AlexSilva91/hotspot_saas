from flask import Blueprint, render_template
from flask_login import login_required
from app.controller.bypass_device_controller.bypass_device_controller import BypassDeviceController

bypass_device_bp = Blueprint("bypass_devices", __name__)

@bypass_device_bp.route("/bypass-devices", methods=["GET"])
@login_required
def list_devices():
    data = BypassDeviceController.list()
    return render_template("bypass_devices/list.html", **data)

@bypass_device_bp.route("/bypass-devices/create", methods=["POST"])
@login_required
def create_device():
    return BypassDeviceController.create()

@bypass_device_bp.route("/bypass-devices/<uuid:device_id>/edit", methods=["POST"])
@login_required
def update_device(device_id):
    return BypassDeviceController.update(device_id)

@bypass_device_bp.route("/bypass-devices/<uuid:device_id>/delete", methods=["POST"])
@login_required
def delete_device(device_id):
    return BypassDeviceController.delete(device_id)

@bypass_device_bp.route("/bypass-devices/<uuid:device_id>/enable", methods=["POST"])
@login_required
def enable_device(device_id):
    return BypassDeviceController.enable(device_id)

@bypass_device_bp.route("/bypass-devices/<uuid:device_id>/change-type", methods=["POST"])
@login_required
def change_type_device(device_id):
    return BypassDeviceController.change_type(device_id)