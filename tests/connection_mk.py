import socket
import asyncio
from app.services.mikrotik_ssh_service import MikroTikSSHService
import os
from dotenv import load_dotenv

load_dotenv()

# =============================
# CORES NO TERMINAL
# =============================
class C:
    RESET  = "\033[0m"
    RED    = "\033[91m"
    GREEN  = "\033[92m"
    YELLOW = "\033[93m"
    BLUE   = "\033[94m"
    CYAN   = "\033[96m"
    GRAY   = "\033[90m"
    BOLD   = "\033[1m"

def ok(msg):    print(f"{C.GREEN}✅ {msg}{C.RESET}")
def err(msg):   print(f"{C.RED}❌ {msg}{C.RESET}")
def info(msg):  print(f"{C.CYAN}ℹ️  {msg}{C.RESET}")
def warn(msg):  print(f"{C.YELLOW}⚠️  {msg}{C.RESET}")
def dbg(msg):   print(f"{C.GRAY}    [DEBUG] {msg}{C.RESET}")
def section(msg): print(f"\n{C.BOLD}{C.BLUE}{'='*55}\n  {msg}\n{'='*55}{C.RESET}")
def step(msg):  print(f"\n{C.BOLD}▶ {msg}{C.RESET}")


# =============================
# ROUTER
# =============================
class Router:
    def __init__(self, ip_address, username, password, port=22):
        self.ip_address = ip_address
        self.username = username
        self.password = password
        self.port = port


# =============================
# TESTE DE PORTA
# =============================
def test_port(host, port=22):
    try:
        s = socket.create_connection((host, port), timeout=3)
        s.close()
        return True
    except Exception as e:
        dbg(f"test_port falhou: {e}")
        return False


# =============================
# EXEC COM DEBUG COMPLETO
# =============================
async def debug_exec(mk, command, label=None):
    """Executa um comando e imprime stdout/stderr brutos antes de qualquer parsing."""
    lbl = label or command
    print(f"\n{C.GRAY}  CMD: {command}{C.RESET}")
    try:
        result = await mk.conn.run(command)
        stdout = result.stdout.strip()
        stderr = result.stderr.strip()
        exit_code = result.exit_status

        dbg(f"exit_code : {exit_code}")
        dbg(f"stdout    : {repr(stdout)}")
        dbg(f"stderr    : {repr(stderr)}")

        if stdout:
            print(f"{C.CYAN}{stdout}{C.RESET}")
        if stderr:
            print(f"{C.YELLOW}  STDERR: {stderr}{C.RESET}")

        return stdout, stderr, exit_code
    except Exception as e:
        err(f"Exceção ao executar [{lbl}]: {type(e).__name__}: {e}")
        return "", str(e), -1


# =============================
# TESTE COMPLETO COM DEBUG
# =============================
async def test_connection(router):
    section(f"TESTE SSH → {router.ip_address}")

    # --- Porta ---
    step("Verificando porta SSH")
    if not test_port(router.ip_address, router.port):
        err("Porta SSH fechada ou inacessível")
        return
    ok(f"Porta {router.port} aberta")

    mk = MikroTikSSHService(
        router.ip_address,
        router.username,
        router.password,
        router.port
    )

    config = {
        # Configurações básicas
        "bridge": "bridge2",
        "lan": "ether2",
        "lan_extras": ["ether3"],
        "wan": "ether1",
        "pool": "hs-pool-20",
        "ranges": "192.168.0.2-192.168.3.254",
        "ip": "192.168.1.1/22",
        "network": "192.168.0.0/22",
        "gateway": "192.168.1.1",
        "profile": "hsprof1",
        "hotspot": "hotspot1",
        "dhcp": "dhcp2",
        "lease_time": "1h",
        "dns_name": "hotspot.meuprovedor.com",
        
        # Perfil de usuário com rate-limit
        "user_profile": {
            "name": "conexao_basica",
            "shared_users": 1,
            "add_mac_cookie": "yes",
            "rate_limit": "10M/5M",  # Download 10Mbps, Upload 5Mbps
            # Outros parâmetros opcionais:
            "idle_timeout": "10m",
            "keepalive_timeout": "2m",
            # "address_list": "clientes_basicos"
        },
        
        # Perfil premium com mais banda
        "user_profile_premium": {
            "name": "conexao_premium",
            "shared_users": 5,
            "add_mac_cookie": "yes",
            "rate_limit": "50M/25M",  # Download 50Mbps, Upload 25Mbps
            "idle_timeout": "30m"
        },
        
        # Usuários com perfis específicos
        "users_with_profiles": [
            {
                "username": "joao_silva",
                "password": "senha123",
                "profile_name": "conexao_basica",
            },
            {
                "username": "maria_santos",
                "password": "senha456",
                "profile_name": "conexao_premium",
            }
        ],
        
        # MACs bypass
        "bypass_macs": [
            "AA:BB:CC:DD:EE:FF",
            "11:22:33:44:55:66"
        ],
        
        # Comentários para MACs
        "bypass_macs_comments": {
            "AA:BB:CC:DD:EE:FF": "Impressora",
            "11:22:33:44:55:66": "Servidor"
        },
        
        # Walled garden
        "walled_garden": [
            {"dst_address": "8.8.8.8", "comment": "Google DNS"},
            {"dst_address": "8.8.4.4", "comment": "Google DNS 2"},
            {"dst_address": "1.1.1.1", "comment": "Cloudflare DNS"}
        ]
    }
    
    try:
        # --- Conexão ---
        step("Conectando via SSH")
        await mk.connect()
        ok("Conectado")

        # =====================================================================
        # BLOCO 0 — LIMPEZA PRÉVIA (reseta o roteador para estado limpo)
        # =====================================================================
        section("BLOCO 0 — LIMPEZA PRÉVIA")

        cleanup_cmds = [
            "/ip hotspot ip-binding remove [find]",
            "/ip hotspot user remove [find name!=default-trial]",
            "/ip hotspot remove [find]",
            "/ip hotspot profile remove [find name!=default]",
            "/ip dhcp-server remove [find]",
            "/ip dhcp-server network remove [find]",
            "/ip address remove [find dynamic=no]",
            "/ip pool remove [find]",
            f"/interface bridge port remove [find bridge={config['bridge']}]",
            f"/interface bridge remove [find name={config['bridge']}]",
            "/ip firewall filter remove [find comment=MGMT_SAFE]",
        ]
        for cmd in cleanup_cmds:
            await debug_exec(mk, cmd)

        ok("Estado limpo — pronto para provisionar")

        # =====================================================================
        # BLOCO 1 — INFO BÁSICA
        # =====================================================================
        section("BLOCO 1 — INFO BÁSICA")

        step("Identity")
        await debug_exec(mk, "/system identity print")

        step("Interfaces")
        await debug_exec(mk, "/interface print")

        step("Pacotes instalados")
        stdout, _, _ = await debug_exec(mk, "/system package print")
        if "hotspot" in stdout.lower():
            ok("Pacote 'hotspot' ENCONTRADO")
        else:
            err("Pacote 'hotspot' NÃO encontrado — isso vai causar falha!")
            warn("Baixe hotspot-6.49.17-mipsbe.npk em mikrotik.com/download")

        step("Recursos atuais: /ip pool")
        await debug_exec(mk, "/ip pool print")

        step("Recursos atuais: /ip address")
        await debug_exec(mk, "/ip address print")

        step("Recursos atuais: /ip dhcp-server")
        await debug_exec(mk, "/ip dhcp-server print")

        step("Recursos atuais: /ip hotspot")
        await debug_exec(mk, "/ip hotspot print")

        step("Recursos atuais: /ip firewall nat")
        await debug_exec(mk, "/ip firewall nat print")

        # =====================================================================
        # BLOCO 2 — TESTE DE CRIAÇÃO MANUAL (SEM safe_add)
        # =====================================================================
        section("BLOCO 2 — TESTE DIRETO DE COMANDOS")

        step("Teste: criar pool diretamente")
        stdout, stderr, code = await debug_exec(mk, "/ip pool add name=debug-pool ranges=10.99.0.1-10.99.0.10")
        await debug_exec(mk, "/ip pool print")

        step("Teste: criar bridge diretamente")
        await debug_exec(mk, "/interface bridge add name=debug-bridge comment=TESTE")
        await debug_exec(mk, "/interface bridge print")

        step("Teste: atribuir IP à bridge")
        await debug_exec(mk, "/ip address add address=10.99.0.1/24 interface=debug-bridge network=10.99.0.0")
        await debug_exec(mk, "/ip address print")

        step("Teste: criar dhcp-server network")
        await debug_exec(mk, "/ip dhcp-server network add address=10.99.0.0/24 gateway=10.99.0.1 comment=TESTE")
        await debug_exec(mk, "/ip dhcp-server network print")

        step("Teste: criar dhcp-server")
        await debug_exec(mk, "/ip dhcp-server add name=debug-dhcp interface=debug-bridge address-pool=debug-pool lease-time=1h disabled=no")
        await debug_exec(mk, "/ip dhcp-server print")

        step("Teste: criar hotspot profile")
        await debug_exec(mk, "/ip hotspot profile add name=debug-prof hotspot-address=10.99.0.1")
        await debug_exec(mk, "/ip hotspot profile print")

        step("Teste: criar hotspot")
        await debug_exec(mk, "/ip hotspot add name=debug-hs interface=debug-bridge address-pool=debug-pool profile=debug-prof disabled=no")
        await debug_exec(mk, "/ip hotspot print")

        # =====================================================================
        # BLOCO 3 — LIMPEZA DO TESTE MANUAL
        # =====================================================================
        section("BLOCO 3 — LIMPEZA DO TESTE MANUAL")

        for cmd in [
            "/ip hotspot remove [find name=debug-hs]",
            "/ip hotspot profile remove [find name=debug-prof]",
            "/ip dhcp-server remove [find name=debug-dhcp]",
            "/ip dhcp-server network remove [find address=10.99.0.0/24]",
            "/ip address remove [find address~\"10.99.0.1\"]",
            "/interface bridge remove [find name=debug-bridge]",
            "/ip pool remove [find name=debug-pool]",
        ]:
            await debug_exec(mk, cmd)

        ok("Limpeza concluída")

        # =====================================================================
        # BLOCO 4 — PROVISIONAMENTO REAL VIA SERVICE
        # =====================================================================
        section("BLOCO 4 — PROVISIONAMENTO VIA MikroTikSSHService")

        step("ensure_hotspot_package")
        try:
            await mk.ensure_hotspot_package()
            ok("Pacote OK")
        except Exception as e:
            err(f"ensure_hotspot_package: {e}")
            raise

        step("ensure_interface_exists: LAN")
        try:
            await mk.ensure_interface_exists(config["lan"])
            ok(f"Interface {config['lan']} existe")
        except Exception as e:
            err(f"ensure_interface_exists({config['lan']}): {e}")
            raise

        step("ensure_interface_exists: WAN")
        try:
            await mk.ensure_interface_exists(config["wan"])
            ok(f"Interface {config['wan']} existe")
        except Exception as e:
            err(f"ensure_interface_exists({config['wan']}): {e}")
            raise

        step("ensure_management_access")
        try:
            await mk.ensure_management_access()
            ok("Acesso SSH/Winbox garantido")
        except Exception as e:
            err(f"ensure_management_access: {e}")
            raise

        step("create_bridge")
        try:
            await mk.create_bridge(config["bridge"])
            ok(f"Bridge '{config['bridge']}' criada")
            await debug_exec(mk, "/interface bridge print")
        except Exception as e:
            err(f"create_bridge: {e}")
            raise

        step("add_interface_to_bridge")
        try:
            await mk.add_interface_to_bridge(config["bridge"], config["lan"])
            ok(f"Interface {config['lan']} adicionada à bridge")
            await debug_exec(mk, "/interface bridge port print")
        except Exception as e:
            err(f"add_interface_to_bridge: {e}")
            raise

        step("assign_ip")
        try:
            network_only = config["network"].split("/")[0]
            await mk.assign_ip(config["bridge"], config["ip"], network_only)
            ok(f"IP {config['ip']} atribuído à bridge")
            await debug_exec(mk, "/ip address print")
        except Exception as e:
            err(f"assign_ip: {e}")
            raise

        step("create_pool")
        try:
            await mk.create_pool(config["pool"], config["ranges"])
            ok(f"Pool '{config['pool']}' criado")
            await debug_exec(mk, "/ip pool print")
        except Exception as e:
            err(f"create_pool: {e}")
            raise

        step("create_dhcp_network")
        try:
            await mk.create_dhcp_network(config["network"], config["gateway"])
            ok(f"DHCP network '{config['network']}' criada")
            await debug_exec(mk, "/ip dhcp-server network print")
        except Exception as e:
            err(f"create_dhcp_network: {e}")
            raise

        step("create_dhcp")
        try:
            await mk.create_dhcp(config["dhcp"], config["bridge"], config["pool"])
            ok(f"DHCP server '{config['dhcp']}' criado")
            await debug_exec(mk, "/ip dhcp-server print")
        except Exception as e:
            err(f"create_dhcp: {e}")
            raise

        step("create_hotspot_profile")
        try:
            await mk.create_hotspot_profile(config["profile"], config["gateway"])
            ok(f"Perfil '{config['profile']}' criado")
            await debug_exec(mk, "/ip hotspot profile print")
        except Exception as e:
            err(f"create_hotspot_profile: {e}")
            raise

        step("create_hotspot")
        try:
            await mk.create_hotspot(config["hotspot"], config["bridge"], config["pool"], config["profile"])
            ok(f"Hotspot '{config['hotspot']}' criado")
            await debug_exec(mk, "/ip hotspot print")
        except Exception as e:
            err(f"create_hotspot: {e}")
            raise

        step("create_nat")
        try:
            await mk.create_nat(config["wan"])
            ok(f"NAT para '{config['wan']}' criado")
            await debug_exec(mk, "/ip firewall nat print")
        except Exception as e:
            err(f"create_nat: {e}")
            raise

        step("create_user_profile")
        try:
            await mk.create_user_profile(**config["user_profile"])
            ok(f"Perfil de usuário '{config['user_profile']['name']}' criado")
            await debug_exec(mk, "/ip hotspot user profile print")
        except Exception as e:
            err(f"create_user_profile: {e}")
            raise

        step("create_user_profile_premium")
        try:
            if "user_profile_premium" in config:
                await mk.create_user_profile(**config["user_profile_premium"])
                ok(f"Perfil de usuário '{config['user_profile_premium']['name']}' criado")
                await debug_exec(mk, "/ip hotspot user profile print")
        except Exception as e:
            err(f"create_user_profile_premium: {e}")

        step("create_users_with_profiles")
        for user in config.get("users_with_profiles", []):
            try:
                await mk.create_user_with_profile(**user)  
                ok(f"Usuário '{user['username']}' criado com perfil '{user['profile_name']}'")
            except Exception as e:
                err(f"create_user_with_profile({user['username']}): {e}")
        await debug_exec(mk, "/ip hotspot user print")

        step("add_bypass_macs")
        for mac in config.get("bypass_macs", []):
            try:
                comment = config.get("bypass_macs_comments", {}).get(mac, "")
                await mk.add_bypass_mac(mac, config["hotspot"], comment)
                ok(f"Bypass MAC {mac} adicionado")
            except Exception as e:
                err(f"add_bypass_mac({mac}): {e}")
        await debug_exec(mk, "/ip hotspot ip-binding print")

        step("add_walled_garden")
        for wg in config.get("walled_garden", []):
            try:
                await mk.add_walled_garden_ip(**wg)
                ok(f"Walled garden {wg['dst_address']} adicionado")
            except Exception as e:
                err(f"add_walled_garden_ip({wg['dst_address']}): {e}")
        await debug_exec(mk, "/ip hotspot walled-garden ip print")

        # =====================================================================
        # BLOCO 5 — VALIDAÇÃO FINAL
        # =====================================================================
        section("BLOCO 5 — VALIDAÇÃO FINAL (diagnostics)")

        step("Executando diagnóstico completo")
        await mk.print_diagnostics()

        ok("PROVISIONAMENTO CONCLUÍDO COM SUCESSO!")

    except Exception as e:
        section("ERRO FATAL")
        err(f"{type(e).__name__}: {e}")
        import traceback
        print(f"{C.GRAY}{traceback.format_exc()}{C.RESET}")

    finally:
        await mk.close()
        print(f"\n{C.GRAY}🔌 Conexão encerrada{C.RESET}\n")


# =============================
# EXECUÇÃO
# =============================
if __name__ == "__main__":
    router = Router(
        ip_address=os.getenv("IP_ADDRESS"),
        username=os.getenv("USERNAME"),
        password=os.getenv("PASSWORD")
    )

    asyncio.run(test_connection(router))