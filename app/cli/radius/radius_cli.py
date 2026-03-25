"""
Comandos CLI para gerenciamento RADIUS
Uso: flask radius <comando>
"""
import click
from flask import current_app
from app.extensions import db
from app.models.hotspot_user import HotspotUser
from app.models.router import Router
from app.services.radius.radius_user_service import RadiusUserService
from app.services.radius.radius_reply_service import RadiusReplyService
from app.services.radius.radius_accounting_service import RadiusAccountingService


def register_radius_cli(app):
    """Registra comandos RADIUS no CLI do Flask"""

    @app.cli.group('radius')
    def radius_group():
        """Comandos para gerenciamento RADIUS"""
        pass

    @radius_group.command('migrate-users')
    @click.option('--dry-run', is_flag=True, help='Apenas simula, não altera banco')
    @click.option('--tenant-id', help='Migrar apenas usuários de um tenant específico (UUID)')
    def migrate_users(dry_run, tenant_id):
        """Migra usuários existentes do hotspot_users para radcheck"""
        click.echo("🚀 Iniciando migração de usuários hotspot para RADIUS...")

        # Busca usuários com filtro opcional por tenant
        query = HotspotUser.query
        if tenant_id:
            # Busca routers do tenant
            routers = Router.query.filter_by(tenant_id=tenant_id).all()
            router_ids = [r.id for r in routers]
            query = query.filter(HotspotUser.router_id.in_(router_ids))
            click.echo(f"📊 Migrando apenas tenant: {tenant_id}")

        users = query.all()
        click.echo(f"📊 Total de usuários encontrados: {len(users)}")

        success_count = 0
        error_count = 0
        skipped_count = 0

        for user in users:
            # Busca tenant_id pelo router
            router = Router.query.get(user.router_id)
            if not router:
                click.echo(f"⚠️  Usuário {user.username} ignorado: router não encontrado (ID: {user.router_id})")
                skipped_count += 1
                continue

            user_tenant_id = router.tenant_id

            if dry_run:
                click.echo(f"🔍 [DRY-RUN] Criaria: {user.username} (tenant: {user_tenant_id}, rate_limit: {user.rate_limit or 'N/A'})")
                success_count += 1
                continue

            try:
                # Verifica se já existe
                existing = RadiusUserService.repository.get_by_username(user.username)
                if existing:
                    click.echo(f"⏭️  Usuário {user.username} já existe no RADIUS (ID: {existing.id}), pulando...")
                    skipped_count += 1
                    continue

                # Cria no RADIUS
                result = RadiusUserService.create_with_rate_limit(
                    username=user.username,
                    password=user.password,
                    rate_limit=user.rate_limit,
                    tenant_id=user_tenant_id
                )

                if result['success']:
                    click.echo(f"✅ Usuário {user.username} migrado com sucesso")
                    success_count += 1
                else:
                    click.echo(f"❌ Erro ao migrar {user.username}: {result.get('errors')}")
                    error_count += 1
            except Exception as e:
                click.echo(f"❌ Exceção ao migrar {user.username}: {str(e)}")
                error_count += 1

        click.echo(f"\n📈 Resumo: {success_count} sucesso(s), {error_count} erro(s), {skipped_count} pulado(s)")

    @radius_group.command('list-users')
    @click.option('--tenant-id', help='Listar usuários de um tenant específico (UUID)')
    def list_users(tenant_id):
        """Lista usuários RADIUS"""
        if tenant_id:
            users = RadiusUserService.repository.get_all_by_tenant(tenant_id)
            click.echo(f"📋 Usuários RADIUS do tenant {tenant_id}:")
        else:
            users = RadiusUserService.repository.get_all()
            click.echo(f"📋 Todos os usuários RADIUS:")

        if not users:
            click.echo("  Nenhum usuário encontrado")
            return

        for user in users:
            click.echo(f"  - {user.username}: {user.attribute}={user.value} (tenant: {user.tenant_id})")

    @radius_group.command('active-sessions')
    @click.option('--tenant-id', help='Listar sessões de um tenant específico (UUID)')
    def active_sessions(tenant_id):
        """Lista sessões ativas"""
        if tenant_id:
            sessions = RadiusAccountingService.repository.get_all_by_tenant(tenant_id)
            sessions = [s for s in sessions if s.is_active]
        else:
            result = RadiusAccountingService.get_active_sessions()
            sessions = result['data'] if result['success'] else []

        click.echo(f"📊 Sessões ativas: {len(sessions)}")
        for session in sessions:
            click.echo(f"  - {session.username} | IP: {session.framedipaddress or 'N/A'} | "
                      f"NAS: {session.nasipaddress} | Início: {session.acctstarttime}")

    @radius_group.command('cleanup')
    @click.option('--days', default=90, help='Dias para manter sessões (padrão: 90)')
    def cleanup_sessions(days):
        """Limpa sessões antigas"""
        click.echo(f"🧹 Limpando sessões com mais de {days} dias...")
        result = RadiusAccountingService.cleanup_old_sessions(days)
        if result['success']:
            click.echo(f"✅ {result['deleted_count']} sessões removidas")
        else:
            click.echo(f"❌ Erro: {result.get('errors')}")

    @radius_group.command('sync-router')
    @click.argument('router_id')
    def sync_router(router_id):
        """Sincroniza usuários de um router com RADIUS"""
        router = Router.query.get(router_id)
        if not router:
            click.echo(f"❌ Router {router_id} não encontrado")
            return

        click.echo(f"🔄 Sincronizando router {router.name}...")

        # Busca usuários do router
        users = HotspotUser.query.filter_by(router_id=router_id).all()
        click.echo(f"📊 Encontrados {len(users)} usuários")

        success_count = 0
        error_count = 0

        for user in users:
            try:
                existing = RadiusUserService.repository.get_by_username(user.username)
                if not existing:
                    result = RadiusUserService.create_with_rate_limit(
                        username=user.username,
                        password=user.password,
                        rate_limit=user.rate_limit,
                        tenant_id=router.tenant_id
                    )
                    if result['success']:
                        click.echo(f"  ✅ {user.username} criado")
                        success_count += 1
                    else:
                        click.echo(f"  ❌ {user.username}: {result.get('errors')}")
                        error_count += 1
                else:
                    click.echo(f"  ⏭️ {user.username} já existe")
                    success_count += 1
            except Exception as e:
                click.echo(f"  ❌ {user.username}: exceção {str(e)}")
                error_count += 1

        click.echo(f"\n📈 Resumo: {success_count} sucesso(s), {error_count} erro(s)")

    @radius_group.command('check-missing')
    def check_missing():
        """Verifica usuários hotspot que não estão no RADIUS"""
        hotspot_users = HotspotUser.query.all()
        radius_usernames = set(u.username for u in RadiusUserService.repository.get_all())

        missing = []
        for user in hotspot_users:
            if user.username not in radius_usernames:
                router = Router.query.get(user.router_id)
                missing.append({
                    'username': user.username,
                    'router': router.name if router else 'N/A',
                    'tenant_id': router.tenant_id if router else 'N/A'
                })

        if missing:
            click.echo(f"⚠️  {len(missing)} usuários não encontrados no RADIUS:")
            for m in missing:
                click.echo(f"  - {m['username']} (router: {m['router']}, tenant: {m['tenant_id']})")
        else:
            click.echo("✅ Todos os usuários hotspot estão sincronizados com RADIUS")