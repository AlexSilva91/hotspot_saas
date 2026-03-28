from flask import Blueprint, render_template
from flask_login import login_required
from app.controller.active_session_controller.active_session_controller import ActiveSessionController

active_session_bp = Blueprint("active_sessions", __name__)

@active_session_bp.route("/active-sessions", methods=["GET"])
@login_required
def list_sessions():
    data = ActiveSessionController.list()
    return render_template("active_sessions/list.html", **data)

@active_session_bp.route("/active-sessions/<uuid:session_id>/disconnect", methods=["POST"])
@login_required
def disconnect_session(session_id):
    return ActiveSessionController.disconnect(session_id)