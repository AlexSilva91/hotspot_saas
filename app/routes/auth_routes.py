from flask import Blueprint, request, render_template, redirect, url_for, session, flash
from werkzeug.security import check_password_hash
from app.repositories.user_repository import UserRepository
from app.services.auth_service import generate_token

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET"])
def login_page():

    return render_template("auth/login.html")


@auth_bp.route("/login", methods=["POST"])
def login():

    email = request.form.get("email")
    password = request.form.get("password")
    
    user = UserRepository.get_by_email(email)

    if not user:
        flash("Credenciais inválidas")
        return redirect(url_for("auth.login_page"))

    if not check_password_hash(user.password_hash, password):
        flash("Credenciais inválidas")
        return redirect(url_for("auth.login_page"))

    token = generate_token(user)

    session["token"] = token
    session["user_id"] = str(user.id)
    session["tenant_id"] = str(user.tenant_id)

    return redirect("/users")

@auth_bp.route("/logout", methods=["GET"])
def logout():
    session.clear()
    flash("Você foi desconectado com sucesso.")
    return redirect(url_for("auth.login_page"))