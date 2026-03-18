from flask import Blueprint, render_template, redirect, url_for, flash
from app.services.active_session_service import ActiveSessionService
from app.controller.base_controller import BaseController
from flask_login import login_required

active_session_bp = Blueprint("active_sessions", __name__)


@active_session_bp.route("/active-sessions", methods=["GET"])
@login_required
def list_sessions():
    result = ActiveSessionService.list()
    sessions = result.get("data", [])

    return render_template(
        "active_sessions/list.html",
        sessions=sessions
    )


@active_session_bp.route("/active-sessions/<uuid:session_id>/disconnect", methods=["POST"])
@login_required
def disconnect_session(session_id):
    result = ActiveSessionService.delete(session_id)

    return BaseController.handle_result(
        result=result,
        success_message="Sessão encerrada!",
        error_default="Erro ao encerrar sessão!",
        redirect_to="active_sessions.list_sessions"
    )