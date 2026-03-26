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
    def migrate_users(dry_run):
        """Migra usuários existentes do hotspot_users para radcheck"""
        click.echo("🚀 Iniciando migração de usuários hotspot para RADIUS...")

        users = HotspotUser.query.all()
        click.echo(f"📊 Total de usuários encontrados: {len(users)}")

        success_count = 0
        error_count = 0
        skipped_count = 0

        for user in users:
            if dry_run:
                click.echo(f"🔍 [DRY-RUN] Criaria: {user.username} (rate_limit: {user.rate_limit or 'N/A'})")
                success_count += 1
                continue

            try:
                # Verifica se já existe
                existing = RadiusUserService.repository.get_by_username(user.username)
                if existing:
                    click.echo(f"⏭️  Usuário {user.username} já existe no RADIUS (ID: {existing.id}), pulando...")
                    skipped_count += 1
                    continue

                # Cria no RADIUS (sem tenant_id)
                result = RadiusUserService.create_with_rate_limit(
                    username=user.username,
                    password=user.password,
                    rate_limit=user.rate_limit
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
    def list_users():
        """Lista usuários RADIUS"""
        users = RadiusUserService.repository.get_all()
        click.echo(f"📋 Todos os usuários RADIUS:")

        if not users:
            click.echo("  Nenhum usuário encontrado")
            return

        for user in users:
            click.echo(f"  - {user.username}: {user.attribute}={user.value}")

    @radius_group.command('active-sessions')
    def active_sessions():
        """Lista sessões ativas"""
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
                        rate_limit=user.rate_limit
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
                    'router': router.name if router else 'N/A'
                })

        if missing:
            click.echo(f"⚠️  {len(missing)} usuários não encontrados no RADIUS:")
            for m in missing:
                click.echo(f"  - {m['username']} (router: {m['router']})")
        else:
            click.echo("✅ Todos os usuários hotspot estão sincronizados com RADIUS")

    @radius_group.command('fix-missing')
    def fix_missing():
        """Corrige usuários faltantes no RADIUS"""
        click.echo("🔧 Verificando usuários faltantes...")
        
        hotspot_users = HotspotUser.query.all()
        radius_usernames = set(u.username for u in RadiusUserService.repository.get_all())

        fixed = 0
        errors = 0

        for user in hotspot_users:
            if user.username not in radius_usernames:
                click.echo(f"  Criando {user.username}...")
                try:
                    result = RadiusUserService.create_with_rate_limit(
                        username=user.username,
                        password=user.password,
                        rate_limit=user.rate_limit
                    )
                    if result['success']:
                        click.echo(f"    ✅ {user.username} criado")
                        fixed += 1
                    else:
                        click.echo(f"    ❌ {user.username}: {result.get('errors')}")
                        errors += 1
                except Exception as e:
                    click.echo(f"    ❌ {user.username}: {str(e)}")
                    errors += 1

        click.echo(f"\n📈 Resumo: {fixed} usuários corrigidos, {errors} erros")

    @radius_group.command('stats')
    def stats():
        """Mostra estatísticas do RADIUS"""
        # Total de usuários - CORRIGIDO
        users_list = RadiusUserService.repository.get_all()
        total_users = len(users_list)  # Usar len() em vez de .count()
        
        # Sessões ativas
        active_result = RadiusAccountingService.get_active_sessions()
        active_sessions = len(active_result['data']) if active_result['success'] else 0
        
        # Tráfego de hoje
        today_traffic = RadiusAccountingService.get_today_traffic()
        today_mb = today_traffic.get('data', {}).get('total_mb', 0) if today_traffic.get('success') else 0
        
        # Últimas autenticações
        from app.models.radius.radius_postauth import RadiusPostAuth
        last_auths = RadiusPostAuth.query.order_by(RadiusPostAuth.authdate.desc()).limit(5).all()
        
        click.echo("\n📊 ESTATÍSTICAS RADIUS")
        click.echo("=" * 50)
        click.echo(f"👥 Usuários cadastrados: {total_users}")
        click.echo(f"🟢 Sessões ativas: {active_sessions}")
        click.echo(f"📈 Tráfego hoje: {today_mb:.2f} MB")
        click.echo(f"\n🕐 Últimas autenticações:")
        for auth in last_auths:
            status = "✅" if auth.reply == "Access-Accept" else "❌"
            click.echo(f"  {status} {auth.username} - {auth.reply} em {auth.authdate.strftime('%H:%M:%S')}")
        click.echo("=" * 50)