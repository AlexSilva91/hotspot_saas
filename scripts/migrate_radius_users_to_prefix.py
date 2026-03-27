# scripts/migrate_radius_users_to_prefix.py

#!/usr/bin/env python3
"""
Script para migrar usuários RADIUS existentes para o formato com prefixo.
Executar: flask shell
>>> exec(open('scripts/migrate_radius_users_to_prefix.py').read())
"""

def migrate():
    from app import create_app
    from app.extensions import db
    from app.models.radius.radius_user import RadiusUser
    from app.models.radius.radius_reply import RadiusReply
    from app.models.radius.radius_accounting import RadiusAccounting
    from app.models.user import User
    from app.services.radius.tenant_prefix_service import TenantPrefixService
    
    app = create_app()
    
    with app.app_context():
        print("🚀 Iniciando migração para formato com prefixo...")
        
        # Mapeia emails para tenants
        user_map = {user.email.lower(): user.tenant_id for user in User.query.all()}
        
        # Busca usuários únicos no RADIUS
        users = db.session.query(RadiusUser.username).distinct().all()
        
        migrated = 0
        skipped = 0
        
        for (username,) in users:
            if TenantPrefixService.SEPARATOR in username:
                print(f"⏭️  Pular: {username} (já tem prefixo)")
                skipped += 1
                continue
            
            tenant_id = user_map.get(username.lower())
            if not tenant_id:
                print(f"⚠️  Ignorar: {username} (sem tenant correspondente)")
                skipped += 1
                continue
            
            new_username = TenantPrefixService.encode(username, tenant_id)
            
            # Atualiza radcheck
            RadiusUser.query.filter_by(username=username).update({'username': new_username})
            
            # Atualiza radreply
            RadiusReply.query.filter_by(username=username).update({'username': new_username})
            
            # Atualiza radacct
            RadiusAccounting.query.filter_by(username=username).update({'username': new_username})
            
            print(f"✅ {username} -> {new_username}")
            migrated += 1
        
        db.session.commit()
        
        print(f"\n📊 Resumo: {migrated} migrados, {skipped} ignorados")
        print("✅ Migração concluída!")

if __name__ == "__main__":
    migrate()