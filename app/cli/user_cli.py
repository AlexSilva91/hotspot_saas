import click
from getpass import getpass
from werkzeug.security import generate_password_hash

from app.extensions import db
from app.models.user import User, UserRole
from app.models.tenant import Tenant


def register_user_cli(app):

    @app.cli.command("create-admin")
    def create_admin():
        """Cria um usuário administrador."""

        click.echo("\n=== Criar Usuário Administrador ===\n")

        tenant_name = click.prompt("Nome do tenant")
        email = click.prompt("Email")

        password = getpass("Senha: ")
        confirm = getpass("Confirmar senha: ")

        if password != confirm:
            click.echo("Erro: senhas não conferem.")
            return

        tenant = Tenant.query.filter_by(name=tenant_name).first()

        if not tenant:
            tenant = Tenant(name=tenant_name)
            db.session.add(tenant)
            db.session.commit()
            click.echo(f"Tenant criado: {tenant_name}")

        existing = User.query.filter_by(
            tenant_id=tenant.id,
            email=email
        ).first()

        if existing:
            click.echo("Usuário já existe neste tenant.")
            return

        user = User(
            tenant_id=tenant.id,
            email=email,
            password_hash=generate_password_hash(password),
            role=UserRole.ADMIN,
            active=True
        )

        db.session.add(user)
        db.session.commit()

        click.echo("\nUsuário administrador criado com sucesso.\n")