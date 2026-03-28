# app/cli/radius/radius_cli.py
"""
Comandos CLI para gerenciamento RADIUS
Uso: flask radius <comando>
"""
import click
import asyncio
from flask import current_app
from app.extensions import db
from app.models.hotspot_user import HotspotUser
from app.models.router import Router
from app.models.tenant import Tenant
from app.services.radius.radius_user_service import RadiusUserService
from app.services.radius.radius_reply_service import RadiusReplyService
from app.services.radius.radius_accounting_service import RadiusAccountingService
from app.services.mikrotik_ssh_service import MikroTikSSHService
from sqlalchemy import func


def register_radius_cli(app):
    """Registra comandos RADIUS no CLI do Flask"""

    @app.cli.group('radius')
    def radius_group():
        """Comandos para gerenciamento RADIUS"""
        pass

    @radius_group.command('migrate-users')
    @click.option('--tenant-id', help='UUID do tenant (opcional, se não informado migra todos)')
    @click.option('--dry-run', is_flag=True, help='Apenas simula, não altera banco')
    def migrate_users(tenant_id, dry_run):
        """Migra usuários existentes do hotspot_users para radcheck com tenant_id automático"""
        click.echo("🚀 Iniciando migração de usuários hotspot para RADIUS...")

        # Determina os tenants a serem migrados
        if tenant_id:
            tenants = [Tenant.query.get(tenant_id)]
            if not tenants[0]:
                click.echo(f"❌ Tenant {tenant_id} não encontrado")
                return
        else:
            tenants = Tenant.query.filter_by(active=True).all()
            if not tenants:
                click.echo("❌ Nenhum tenant ativo encontrado")
                return

        total_success = 0
        total_error = 0
        total_skipped = 0

        for tenant in tenants:
            click.echo(f"\n📌 Processando tenant: {tenant.name} (ID: {tenant.id})")

            # Busca routers do tenant
            routers = Router.query.filter_by(tenant_id=tenant.id).all()
            if not routers:
                click.echo(f"  ⚠️  Nenhum router encontrado para este tenant")
                continue

            router_ids = [r.id for r in routers]
            users = HotspotUser.query.filter(HotspotUser.router_id.in_(router_ids)).all()
            click.echo(f"  📊 Total de usuários encontrados: {len(users)}")

            success_count = 0
            error_count = 0
            skipped_count = 0

            for user in users:
                if dry_run:
                    click.echo(f"    🔍 [DRY-RUN] Criaria: {user.username} | rate_limit: {user.rate_limit or 'N/A'} | tenant: {tenant.name}")
                    success_count += 1
                    continue

                try:
                    # Verifica se já existe para este tenant
                    existing = RadiusUserService.repository.get_by_username(user.username)
                    if existing and existing.tenant_id == tenant.id:
                        click.echo(f"    ⏭️  Usuário {user.username} já existe no RADIUS (ID: {existing.id}), pulando...")
                        skipped_count += 1
                        continue

                    # Cria no RADIUS com tenant_id
                    result = RadiusUserService.create_with_rate_limit(
                        username=user.username,
                        password=user.password,
                        rate_limit=user.rate_limit,
                        tenant_id=tenant.id
                    )

                    if result['success']:
                        click.echo(f"    ✅ Usuário {user.username} migrado com sucesso")
                        success_count += 1
                    else:
                        click.echo(f"    ❌ Erro ao migrar {user.username}: {result.get('errors')}")
                        error_count += 1
                except Exception as e:
                    click.echo(f"    ❌ Exceção ao migrar {user.username}: {str(e)}")
                    error_count += 1

            click.echo(f"\n  📈 Resumo do tenant {tenant.name}: {success_count} sucesso(s), {error_count} erro(s), {skipped_count} pulado(s)")
            total_success += success_count
            total_error += error_count
            total_skipped += skipped_count

        click.echo(f"\n{'='*50}")
        click.echo(f"📊 MIGRAÇÃO TOTAL FINALIZADA")
        click.echo(f"  ✅ Sucessos: {total_success}")
        click.echo(f"  ❌ Erros: {total_error}")
        click.echo(f"  ⏭️  Pulados: {total_skipped}")
        click.echo(f"{'='*50}")

    @radius_group.command('list-users')
    @click.option('--tenant-id', help='UUID do tenant (se não informado, lista todos)')
    def list_users(tenant_id):
        """Lista usuários RADIUS por tenant"""
        from app.models.radius.radius_user import RadiusUser
        
        if tenant_id:
            tenant = Tenant.query.get(tenant_id)
            if not tenant:
                click.echo(f"❌ Tenant {tenant_id} não encontrado")
                return
            click.echo(f"📋 Usuários RADIUS do tenant: {tenant.name}")
            users = RadiusUser.query.filter_by(tenant_id=tenant.id).all()
        else:
            click.echo("📋 Todos os usuários RADIUS:")
            users = RadiusUserService.repository.get_all()

        if not users:
            click.echo("  Nenhum usuário encontrado")
            return

        for user in users:
            tenant_info = f"tenant: {str(user.tenant_id)[:8]}" if user.tenant_id else "sem tenant"
            click.echo(f"  - {user.username} ({tenant_info}): {user.attribute}={user.value} | {'✅ Ativo' if user.is_active else '❌ Bloqueado'}")

    @radius_group.command('active-sessions')
    @click.option('--tenant-id', help='UUID do tenant (se não informado, lista todos)')
    def active_sessions(tenant_id):
        """Lista sessões ativas por tenant"""
        from app.models.radius.radius_accounting import RadiusAccounting
        
        if tenant_id:
            tenant = Tenant.query.get(tenant_id)
            if not tenant:
                click.echo(f"❌ Tenant {tenant_id} não encontrado")
                return
            click.echo(f"📊 Sessões ativas do tenant: {tenant.name}")
            sessions = RadiusAccounting.query.filter(
                RadiusAccounting.tenant_id == tenant.id,
                RadiusAccounting.acctstoptime.is_(None)
            ).all()
        else:
            result = RadiusAccountingService.get_active_sessions()
            sessions = result['data'] if result['success'] else []

        click.echo(f"📊 Total de sessões ativas: {len(sessions)}")
        for session in sessions:
            click.echo(f"  - {session.username} | IP: {session.framedipaddress or 'N/A'} | "
                      f"NAS: {session.nasipaddress} | Início: {session.acctstarttime}")

    @radius_group.command('cleanup')
    @click.option('--days', default=90, help='Dias para manter sessões (padrão: 90)')
    @click.option('--tenant-id', help='UUID do tenant (se não informado, limpa todos)')
    def cleanup_sessions(days, tenant_id):
        """Limpa sessões antigas por tenant"""
        from app.models.radius.radius_accounting import RadiusAccounting
        from datetime import datetime, timedelta
        
        cutoff = datetime.now() - timedelta(days=days)
        
        if tenant_id:
            tenant = Tenant.query.get(tenant_id)
            if not tenant:
                click.echo(f"❌ Tenant {tenant_id} não encontrado")
                return
            click.echo(f"🧹 Limpando sessões do tenant {tenant.name} com mais de {days} dias...")
            
            count = RadiusAccounting.query.filter(
                RadiusAccounting.tenant_id == tenant.id,
                RadiusAccounting.acctstarttime < cutoff,
                RadiusAccounting.acctstoptime.isnot(None)
            ).delete()
            db.session.commit()
            
            click.echo(f"✅ {count} sessões removidas")
        else:
            click.echo(f"🧹 Limpando todas as sessões com mais de {days} dias...")
            count = RadiusAccounting.query.filter(
                RadiusAccounting.acctstarttime < cutoff,
                RadiusAccounting.acctstoptime.isnot(None)
            ).delete()
            db.session.commit()
            click.echo(f"✅ {count} sessões removidas")

    @radius_group.command('sync-router')
    @click.argument('router_id')
    @click.option('--dry-run', is_flag=True, help='Apenas simula, não altera banco')
    def sync_router(router_id, dry_run):
        """Sincroniza usuários de um router com RADIUS (tenant_id automático)"""
        router = Router.query.get(router_id)
        if not router:
            click.echo(f"❌ Router {router_id} não encontrado")
            return

        click.echo(f"🔄 Sincronizando router {router.name} do tenant {router.tenant.name}...")

        # Busca usuários do router
        users = HotspotUser.query.filter_by(router_id=router_id).all()
        click.echo(f"📊 Encontrados {len(users)} usuários")

        success_count = 0
        error_count = 0

        for user in users:
            if dry_run:
                click.echo(f"🔍 [DRY-RUN] Sincronizaria: {user.username}")
                success_count += 1
                continue

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
                    if existing.tenant_id != router.tenant_id:
                        existing.tenant_id = router.tenant_id
                        db.session.commit()
                        click.echo(f"  🔄 {user.username}: tenant_id atualizado")
                    else:
                        click.echo(f"  ⏭️ {user.username} já existe")
                    success_count += 1
            except Exception as e:
                click.echo(f"  ❌ {user.username}: exceção {str(e)}")
                error_count += 1

        click.echo(f"\n📈 Resumo: {success_count} sucesso(s), {error_count} erro(s)")

    @radius_group.command('check-missing')
    @click.option('--tenant-id', help='UUID do tenant (se não informado, verifica todos)')
    def check_missing(tenant_id):
        """Verifica usuários hotspot que não estão no RADIUS por tenant"""
        from app.models.radius.radius_user import RadiusUser
        
        if tenant_id:
            tenant = Tenant.query.get(tenant_id)
            if not tenant:
                click.echo(f"❌ Tenant {tenant_id} não encontrado")
                return
            tenants_to_check = [tenant]
        else:
            tenants_to_check = Tenant.query.filter_by(active=True).all()

        total_missing = 0
        
        for tenant in tenants_to_check:
            click.echo(f"\n🔍 Verificando usuários faltantes no tenant: {tenant.name}")
            
            routers = Router.query.filter_by(tenant_id=tenant.id).all()
            router_ids = [r.id for r in routers]
            hotspot_users = HotspotUser.query.filter(HotspotUser.router_id.in_(router_ids)).all()
            
            radius_usernames = set(
                u.username for u in RadiusUser.query.filter_by(tenant_id=tenant.id).all()
            )

            missing = []
            for user in hotspot_users:
                if user.username not in radius_usernames:
                    router = Router.query.get(user.router_id)
                    missing.append({
                        'username': user.username,
                        'router': router.name if router else 'N/A'
                    })

            if missing:
                click.echo(f"  ⚠️  {len(missing)} usuários não encontrados no RADIUS:")
                for m in missing:
                    click.echo(f"    - {m['username']} (router: {m['router']})")
                total_missing += len(missing)
            else:
                click.echo(f"  ✅ Todos os usuários hotspot estão sincronizados")

        if total_missing == 0 and not tenant_id:
            click.echo(f"\n✅ Todos os tenants estão sincronizados!")
        elif total_missing > 0:
            click.echo(f"\n⚠️  Total de usuários faltantes: {total_missing}")

    @radius_group.command('fix-missing')
    @click.option('--tenant-id', help='UUID do tenant (se não informado, corrige todos)')
    @click.option('--dry-run', is_flag=True, help='Apenas simula, não altera banco')
    def fix_missing(tenant_id, dry_run):
        """Corrige usuários faltantes no RADIUS"""
        from app.models.radius.radius_user import RadiusUser
        
        if tenant_id:
            tenant = Tenant.query.get(tenant_id)
            if not tenant:
                click.echo(f"❌ Tenant {tenant_id} não encontrado")
                return
            tenants_to_fix = [tenant]
        else:
            tenants_to_fix = Tenant.query.filter_by(active=True).all()

        total_fixed = 0
        total_errors = 0

        for tenant in tenants_to_fix:
            click.echo(f"\n🔧 Corrigindo usuários faltantes no tenant: {tenant.name}")
            
            routers = Router.query.filter_by(tenant_id=tenant.id).all()
            router_ids = [r.id for r in routers]
            hotspot_users = HotspotUser.query.filter(HotspotUser.router_id.in_(router_ids)).all()
            
            radius_usernames = set(
                u.username for u in RadiusUser.query.filter_by(tenant_id=tenant.id).all()
            )

            fixed = 0
            errors = 0

            for user in hotspot_users:
                if user.username not in radius_usernames:
                    if dry_run:
                        click.echo(f"  🔍 [DRY-RUN] Criaria: {user.username}")
                        fixed += 1
                        continue
                        
                    click.echo(f"  Criando {user.username}...")
                    try:
                        result = RadiusUserService.create_with_rate_limit(
                            username=user.username,
                            password=user.password,
                            rate_limit=user.rate_limit,
                            tenant_id=tenant.id
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

            click.echo(f"  📈 Resumo do tenant {tenant.name}: {fixed} corrigidos, {errors} erros")
            total_fixed += fixed
            total_errors += errors

        if dry_run:
            click.echo(f"\n📈 [DRY-RUN] Seriam corrigidos: {total_fixed} usuários")
        else:
            click.echo(f"\n📈 Resumo total: {total_fixed} usuários corrigidos, {total_errors} erros")

    @radius_group.command('stats')
    @click.option('--tenant-id', help='UUID do tenant (se não informado, mostra todos)')
    def stats(tenant_id):
        """Mostra estatísticas do RADIUS por tenant"""
        if tenant_id:
            tenant = Tenant.query.get(tenant_id)
            if not tenant:
                click.echo(f"❌ Tenant {tenant_id} não encontrado")
                return
            _show_tenant_stats(tenant)
        else:
            click.echo("\n📊 ESTATÍSTICAS RADIUS - TODOS OS TENANTS")
            click.echo("=" * 60)
            tenants = Tenant.query.filter_by(active=True).all()
            for tenant in tenants:
                _show_tenant_stats(tenant, show_header=True)
            click.echo("=" * 60)

    @radius_group.command('block-user')
    @click.argument('username')
    @click.option('--tenant-id', help='UUID do tenant (opcional)')
    @click.option('--disconnect', is_flag=True, help='Desconecta sessões ativas do usuário')
    def block_user(username, tenant_id, disconnect):
        """Bloqueia um usuário RADIUS e opcionalmente desconecta do MikroTik"""

        from app.models.radius.radius_user import RadiusUser
        from app.models.radius.radius_accounting import RadiusAccounting
        from app.models.router import Router
        from app.models.tenant import Tenant
        from app.services.mikrotik_ssh_service import MikroTikSSHService
        from app.extensions import db
        import asyncio
        from datetime import datetime

        # =========================================================================
        # RESOLVE TENANT
        # =========================================================================

        if not tenant_id:
            user = RadiusUser.query.filter_by(username=username).first()
            if user and user.tenant_id:
                tenant_id = user.tenant_id
                tenant = Tenant.query.get(tenant_id)
            else:
                tenant = Tenant.query.first()
                if tenant:
                    tenant_id = tenant.id
                    click.echo(f"⚠️  Tenant não especificado, usando: {tenant.name}")
                else:
                    click.echo("❌ Nenhum tenant encontrado")
                    return
        else:
            tenant = Tenant.query.get(tenant_id)

        if not tenant:
            click.echo(f"❌ Tenant {tenant_id} não encontrado")
            return

        # =========================================================================
        # BLOQUEIA NO RADIUS
        # =========================================================================

        result = RadiusUserService.repository.block_user(username)

        if not result:
            click.echo(f"❌ Usuário {username} não encontrado no RADIUS")
            return

        click.echo(f"✅ Usuário {username} bloqueado no RADIUS (tenant: {tenant.name})")

        # =========================================================================
        # DISCONNECT (SEM DEPENDER DE SESSÃO)
        # =========================================================================

        if disconnect:
            click.echo(f"🔌 Desconectando {username} completamente dos MikroTiks...")

            routers = Router.query.filter_by(tenant_id=tenant_id).all()

            if not routers:
                click.echo("❌ Nenhum router encontrado para este tenant")
                return

            disconnected = 0

            for router in routers:
                try:
                    async def disconnect_full():
                        ssh = MikroTikSSHService(
                            host=router.ip_address,
                            username=router.username,
                            password=router.password
                        )
                        await ssh.connect()

                        # 🔥 SEM validação — EXECUTA DIRETO
                        await ssh.full_disconnect_hotspot_user(username)

                        await ssh.close()

                    asyncio.run(disconnect_full())

                    click.echo(f"  ✅ Comando enviado para {router.name}")
                    disconnected += 1

                except Exception as e:
                    click.echo(f"  ❌ Erro no router {router.name}: {e}")

            # =========================================================================
            # ATUALIZA BANCO (INDEPENDENTE DO MIKROTIK)
            # =========================================================================

            sessions = RadiusAccounting.query.filter(
                RadiusAccounting.username == username,
                RadiusAccounting.acctstoptime.is_(None)
            ).all()

            for session in sessions:
                session.acctstoptime = datetime.now()
                session.acctterminatecause = 'Admin-Reset'

            db.session.commit()

            click.echo(f"  📊 Comando enviado para {disconnected} router(s)")

        # =========================================================================
        # FINAL
        # =========================================================================

        click.echo(f"✅ Operação concluída!")
        
    @radius_group.command('unblock-user')
    @click.argument('username')
    @click.option('--tenant-id', help='UUID do tenant (opcional)')
    @click.option('--password', default=None, help='Senha do usuário (se não informada, usa a do RADIUS)')
    @click.option('--profile', default=None, help='Perfil do usuário no MikroTik')
    @click.option('--rate-limit', default=None, help='Limite de banda')
    def unblock_user(username, tenant_id, password, profile, rate_limit):
        """Desbloqueia um usuário RADIUS e recria no MikroTik"""
        from app.models.radius.radius_user import RadiusUser
        from app.models.radius.radius_reply import RadiusReply
        
        # Se não passou tenant-id, tenta descobrir
        if not tenant_id:
            user = RadiusUser.query.filter_by(username=username).first()
            if user and user.tenant_id:
                tenant_id = user.tenant_id
                tenant = Tenant.query.get(tenant_id)
            else:
                tenant = Tenant.query.first()
                if tenant:
                    tenant_id = tenant.id
                    click.echo(f"⚠️  Tenant não especificado, usando: {tenant.name}")
                else:
                    click.echo("❌ Nenhum tenant encontrado")
                    return
        else:
            tenant = Tenant.query.get(tenant_id)
        
        if not tenant:
            click.echo(f"❌ Tenant {tenant_id} não encontrado")
            return
        
        # 1. Buscar usuário no RADIUS
        radius_user = RadiusUser.query.filter_by(username=username).first()
        if not radius_user:
            click.echo(f"❌ Usuário {username} não encontrado no RADIUS")
            return
        
        # 2. Desbloquear no RADIUS
        result = RadiusUserService.repository.unblock_user(username)
        
        if not result:
            click.echo(f"❌ Erro ao desbloquear {username} no RADIUS")
            return
        
        click.echo(f"✅ Usuário {username} desbloqueado no RADIUS (tenant: {tenant.name})")
        
        # 3. Determinar senha
        user_password = password
        if not user_password:
            user_password = radius_user.value
            click.echo(f"  Usando senha do RADIUS: {user_password}")
        
        # 4. Buscar rate limit do radreply
        if not rate_limit:
            rate_reply = RadiusReply.query.filter_by(
                username=username,
                attribute="Mikrotik-Rate-Limit"
            ).first()
            if rate_reply:
                rate_limit = rate_reply.value
                click.echo(f"  Usando rate limit do RADIUS: {rate_limit}")
        
        # 5. Buscar routers do tenant
        routers = Router.query.filter_by(tenant_id=tenant.id).all()
        if not routers:
            click.echo(f"⚠️  Nenhum router encontrado para o tenant {tenant.name}")
            return
        
        click.echo(f"🔄 Recriando usuário {username} nos routers...")
        
        recreated = 0
        for router in routers:
            try:
                async def recreate_user():
                    ssh = MikroTikSSHService(
                        host=router.ip_address,
                        username=router.username,
                        password=router.password
                    )
                    await ssh.connect()
                    result = await ssh.full_unblock_hotspot_user(
                        username=username,
                        password=user_password,
                        server="all",
                        profile=profile,
                        rate_limit=rate_limit
                    )
                    await ssh.close()
                    return result
                
                success = asyncio.run(recreate_user())
                if success:
                    click.echo(f"  ✅ Usuário {username} recriado no router {router.name}")
                    recreated += 1
                else:
                    click.echo(f"  ⚠️  Falha ao recriar {username} no router {router.name}")
                    
            except Exception as e:
                click.echo(f"  ❌ Erro no router {router.name}: {e}")
        
        click.echo(f"📊 Usuário recriado em {recreated} de {len(routers)} router(s)")
        click.echo(f"✅ Operação concluída!")

    @radius_group.command('disconnect-user')
    @click.argument('username')
    @click.option('--tenant-id', help='UUID do tenant (opcional)')
    def disconnect_user(username, tenant_id):
        """Desconecta um usuário de todas as sessões ativas no MikroTik"""
        from app.models.radius.radius_accounting import RadiusAccounting
        
        if tenant_id:
            tenant = Tenant.query.get(tenant_id)
        else:
            tenant = Tenant.query.first()
        
        if not tenant:
            click.echo("❌ Nenhum tenant encontrado")
            return
        
        # Buscar sessões ativas
        sessions = RadiusAccounting.query.filter(
            RadiusAccounting.username == username,
            RadiusAccounting.acctstoptime.is_(None)
        ).all()
        
        if not sessions:
            click.echo(f"ℹ️  Nenhuma sessão ativa encontrada para {username}")
            return
        
        click.echo(f"🔌 Desconectando {username} de {len(sessions)} sessão(ões)...")
        
        disconnected = 0
        for session in sessions:
            router = Router.query.filter_by(ip_address=str(session.nasipaddress)).first()
            if not router:
                click.echo(f"  ⚠️  Router não encontrado para NAS {session.nasipaddress}")
                continue
            
            try:
                async def disconnect():
                    ssh = MikroTikSSHService(
                        host=router.ip_address,
                        username=router.username,
                        password=router.password
                    )
                    await ssh.connect()
                    result = await ssh.disconnect_hotspot_user(username)
                    await ssh.close()
                    return result
                
                if asyncio.run(disconnect()):
                    click.echo(f"  ✅ Desconectado do router {router.name}")
                    disconnected += 1
                    
                    # Atualizar sessão no banco
                    from datetime import datetime
                    session.acctstoptime = datetime.now()
                    session.acctterminatecause = 'Admin-Reset'
                    db.session.commit()
                else:
                    click.echo(f"  ⚠️  Usuário não encontrado no router {router.name}")
                    
            except Exception as e:
                click.echo(f"  ❌ Erro no router {router.name}: {e}")
        
        click.echo(f"\n📊 Desconectado de {disconnected} router(s)")

    @radius_group.command('list-tenants')
    def list_tenants():
        """Lista todos os tenants disponíveis"""
        tenants = Tenant.query.all()
        if not tenants:
            click.echo("❌ Nenhum tenant encontrado")
            return
        
        click.echo("\n📋 TENANTS DISPONÍVEIS:")
        click.echo("=" * 80)
        for tenant in tenants:
            click.echo(f"  ID: {tenant.id}")
            click.echo(f"  Nome: {tenant.name}")
            click.echo(f"  Plano: {tenant.plan.name if tenant.plan else 'N/A'}")
            click.echo(f"  Ativo: {'✅' if tenant.active else '❌'}")
            click.echo("-" * 40)


def _show_tenant_stats(tenant, show_header=False):
    """Exibe estatísticas de um tenant específico"""
    from app.models.radius.radius_user import RadiusUser
    from app.models.radius.radius_accounting import RadiusAccounting
    from app.models.radius.radius_postauth import RadiusPostAuth
    from datetime import datetime
    
    total_users = RadiusUser.query.filter_by(tenant_id=tenant.id).count()
    active_users = RadiusUser.query.filter_by(
        tenant_id=tenant.id,
        is_active=True
    ).count()
    
    active_sessions = RadiusAccounting.query.filter(
        RadiusAccounting.tenant_id == tenant.id,
        RadiusAccounting.acctstoptime.is_(None)
    ).count()
    
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_traffic = db.session.query(
        func.coalesce(func.sum(RadiusAccounting.acctinputoctets), 0).label('input'),
        func.coalesce(func.sum(RadiusAccounting.acctoutputoctets), 0).label('output')
    ).filter(
        RadiusAccounting.tenant_id == tenant.id,
        RadiusAccounting.acctstarttime >= today
    ).first()
    
    total_mb = ((today_traffic.input or 0) + (today_traffic.output or 0)) / (1024 * 1024)
    today_auths = RadiusPostAuth.query.filter(
        RadiusPostAuth.tenant_id == tenant.id,
        RadiusPostAuth.authdate >= today
    ).count()
    
    last_auths = RadiusPostAuth.query.filter(
        RadiusPostAuth.tenant_id == tenant.id
    ).order_by(RadiusPostAuth.authdate.desc()).limit(5).all()
    
    if show_header:
        click.echo(f"\n📌 {tenant.name}")
        click.echo("-" * 40)
    else:
        click.echo(f"\n📊 ESTATÍSTICAS RADIUS - {tenant.name}")
        click.echo("=" * 50)
    
    click.echo(f"👥 Usuários cadastrados: {total_users} ({active_users} ativos)")
    click.echo(f"🟢 Sessões ativas: {active_sessions}")
    click.echo(f"📈 Tráfego hoje: {total_mb:.2f} MB")
    click.echo(f"🔐 Autenticações hoje: {today_auths}")
    
    if last_auths:
        click.echo(f"\n🕐 Últimas autenticações:")
        for auth in last_auths:
            status = "✅" if auth.reply == "Access-Accept" else "❌"
            click.echo(f"  {status} {auth.username} - {auth.reply} em {auth.authdate.strftime('%H:%M:%S')}")
    else:
        click.echo(f"\n🕐 Nenhuma autenticação recente")
    
    if not show_header:
        click.echo("=" * 50)