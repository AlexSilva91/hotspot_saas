from flask import Blueprint, render_template, redirect, url_for, flash
from app.services.active_session_service import ActiveSessionService
from app.decorators.login_required import login_required

active_session_bp = Blueprint("active_sessions", __name__)


@active_session_bp.route("/active-sessions", methods=["GET"])
@login_required
def list_sessions():

    sessions = ActiveSessionService.list_sessions()

    return render_template(
        "active_sessions/list.html",
        sessions=sessions
    )


@active_session_bp.route("/active-sessions/<uuid:session_id>/disconnect", methods=["POST"])
@login_required
def disconnect_session(session_id):

    try:

        ActiveSessionService.delete_session(session_id)

        flash("Sessão encerrada!", "success")

    except Exception:

        flash("Erro ao encerrar sessão!", "error")

    return redirect(url_for("active_sessions.list_sessions"))