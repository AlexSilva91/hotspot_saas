import asyncio
import asyncssh


class MikroTikSSHService:
    """
    Serviço completo para provisionamento de Hotspot MikroTik via SSH.
    
    Funcionalidades:
    - Conexão SSH com suporte a algoritmos legados (RouterOS antigo)
    - Provisionamento completo de Hotspot (bridge, pool, DHCP, NAT, usuários, bypass)
    - Criação de perfis de usuário hotspot (/ip hotspot user profile)
    - Rollback automático em caso de falha
    - Validações antes de cada operação
    - Suporte a múltiplas interfaces LAN
    - Remoção completa do Hotspot
    """

    def __init__(self, host, username, password, port=22, timeout=10):
        self.host = host
        self.username = username
        self.password = password
        self.port = port
        self.timeout = timeout
        self.conn = None
        self.rollback_stack = []

    # =========================================================================
    # CONEXÃO
    # =========================================================================

    async def connect(self):
        """Estabelece conexão SSH com o RouterOS."""
        self.conn = await asyncssh.connect(
            self.host,
            port=self.port,
            username=self.username,
            password=self.password,
            known_hosts=None,
            login_timeout=self.timeout,
            kex_algs=[
                "diffie-hellman-group14-sha1",
                "diffie-hellman-group1-sha1",
                "diffie-hellman-group14-sha256",
            ],
            encryption_algs=[
                "aes128-ctr",
                "aes192-ctr",
                "aes256-ctr",
                "aes128-cbc",
            ],
            server_host_key_algs=["ssh-rsa"],
        )

    async def close(self):
        """Encerra a conexão SSH."""
        if self.conn:
            self.conn.close()
            await self.conn.wait_closed()
            self.conn = None

    # =========================================================================
    # EXECUÇÃO DE COMANDOS
    # =========================================================================

    async def exec(self, command):
        """
        Executa um comando no RouterOS e retorna o stdout.
        Lança Exception em caso de erros conhecidos.
        """
        result = await self.conn.run(command)

        out = result.stdout.strip()
        err = result.stderr.strip()
        full = f"{out} {err}".lower()

        # Erros ignorados (comportamento normal do RouterOS)
        ignored_patterns = [
            "no such item",
        ]
        if any(p in full for p in ignored_patterns):
            return out

        # Erros que devem lançar exceção
        error_patterns = [
            "failure",
            "bad command",
            "syntax error",
            "no such command",
            "invalid value",
            "already have such",
            "expected end of command",
            "ambiguous value",
        ]
        if any(e in full for e in error_patterns):
            raise Exception(f"Erro no comando [{command}]: {out or err}")

        return out

    async def exec_silent(self, command):
        """Executa comando ignorando qualquer erro (uso interno)."""
        try:
            return await self.exec(command)
        except Exception:
            return ""

    # =========================================================================
    # HELPERS
    # =========================================================================

    async def exists(self, path, where):
        """
        Verifica se um recurso existe no RouterOS.

        Estratégia: usa 'print' com count-only para evitar problemas
        de parsing do 'where' com hífens, aspas e operadores especiais.
        Faz grep no output do print sem where, que é mais confiável.
        """
        try:
            result = await self.conn.run(f"{path} print")
            output = result.stdout.strip()
            if not output:
                return False

            for condition in where.split(" "):
                if "=" not in condition:
                    continue
                _, val = condition.split("=", 1)
                val = val.strip('"').lstrip("~")
                if val and val not in output:
                    return False
            return True
        except Exception:
            return False

    async def safe_add(self, path, where, command, rollback_cmd=None):
        """
        Adiciona um recurso somente se ele ainda não existir.
        Registra rollback_cmd na pilha para desfazer em caso de falha.
        """
        if await self.exists(path, where):
            return  # já existe, ignora

        await self.exec(command)

        # Pequena pausa para o RouterOS confirmar a escrita
        await asyncio.sleep(0.3)

        if not await self.exists(path, where):
            raise Exception(f"Falha ao criar: {path} (where={where})")

        if rollback_cmd:
            self.rollback_stack.append(rollback_cmd)

    async def safe_remove(self, command):
        """Remove um recurso ignorando erros de 'não existe'."""
        try:
            await self.exec(command)
        except Exception as e:
            if "no such item" not in str(e).lower():
                raise

    # =========================================================================
    # ROLLBACK
    # =========================================================================

    async def rollback(self):
        """Desfaz todas as operações registradas na pilha (ordem inversa)."""
        print("⚠️  Executando rollback...")
        for cmd in reversed(self.rollback_stack):
            await self.safe_remove(cmd)
        self.rollback_stack.clear()
        print("✅ Rollback concluído")

    # =========================================================================
    # VALIDAÇÕES
    # =========================================================================

    async def ensure_hotspot_package(self):
        """Garante que o pacote hotspot está instalado e ativo."""
        packages = await self.exec("/system package print")

        if "hotspot" not in packages.lower():
            raise Exception(
                "Pacote 'hotspot' não está instalado neste RouterOS. "
                "Instale via /system package e reinicie o equipamento."
            )

    async def ensure_interface_exists(self, name):
        """Garante que uma interface existe no roteador."""
        if not await self.exists("/interface", f"name={name}"):
            raise Exception(
                f"Interface '{name}' não encontrada. "
                f"Verifique as interfaces disponíveis com /interface print."
            )

    async def ensure_management_access(self):
        """
        Garante que SSH e Winbox continuem acessíveis mesmo após
        o hotspot redirecionar o tráfego da bridge.
        """
        services = await self.exec("/ip service print")

        ssh_port = "22"
        winbox_port = "8291"

        for line in services.splitlines():
            parts = line.split()
            if len(parts) < 3:
                continue
            name = parts[1] if len(parts) > 1 else ""
            port = parts[2] if len(parts) > 2 else ""
            if name == "ssh":
                ssh_port = port
            elif name == "winbox":
                winbox_port = port

        chains = ["input", "hs-input"]
        ports = [ssh_port, winbox_port]

        for chain in chains:
            for port in ports:
                if not await self.exists("/ip firewall filter", f"chain={chain} protocol=tcp dst-port={port}"):
                    await self.exec(
                        f"/ip firewall filter add chain={chain} protocol=tcp "
                        f'dst-port={port} action=accept place-before=0 comment="MGMT_SAFE"'
                    )

    # =========================================================================
    # CRIAÇÃO DE RECURSOS
    # =========================================================================

    async def create_bridge(self, name, comment="HOTSPOT"):
        """Cria uma bridge se não existir."""
        await self.safe_add(
            "/interface bridge",
            f"name={name}",
            f'/interface bridge add name={name} comment="{comment}"',
            f"/interface bridge remove [find name={name}]",
        )

    async def add_interface_to_bridge(self, bridge, interface):
        """Adiciona uma interface à bridge."""
        await self.safe_add(
            "/interface bridge port",
            f"bridge={bridge} interface={interface}",
            f"/interface bridge port add bridge={bridge} interface={interface}",
            f"/interface bridge port remove [find bridge={bridge} interface={interface}]",
        )

    async def create_pool(self, name, ranges):
        """Cria um pool de IPs."""
        await self.safe_add(
            "/ip pool",
            f"name={name}",
            f"/ip pool add name={name} ranges={ranges}",
            f"/ip pool remove [find name={name}]",
        )

    async def assign_ip(self, interface, address, network):
        """Atribui um endereço IP a uma interface."""
        ip_only = address.split("/")[0]
        await self.safe_add(
            "/ip address",
            f"address={ip_only}",
            f"/ip address add address={address} interface={interface} network={network}",
            f"/ip address remove [find interface={interface} address~\"{ip_only}\"]",
        )

    async def create_dhcp_network(self, network, gateway, comment="hotspot network"):
        """Cria uma rede DHCP."""
        await self.safe_add(
            "/ip dhcp-server network",
            f"address={network}",
            f'/ip dhcp-server network add address={network} gateway={gateway} comment="{comment}"',
            f"/ip dhcp-server network remove [find address={network}]",
        )

    async def create_dhcp(self, name, interface, pool, lease_time="1h"):
        """Cria um servidor DHCP."""
        await self.safe_add(
            "/ip dhcp-server",
            f"name={name}",
            f"/ip dhcp-server add name={name} interface={interface} "
            f"address-pool={pool} lease-time={lease_time} disabled=no",
            f"/ip dhcp-server remove [find name={name}]",
        )

    async def create_hotspot_profile(self, name, address, dns_name=""):
        """Cria um perfil de hotspot."""
        dns_part = f" dns-name={dns_name}" if dns_name else ""
        await self.safe_add(
            "/ip hotspot profile",
            f"name={name}",
            f"/ip hotspot profile add name={name} hotspot-address={address}{dns_part}",
            f"/ip hotspot profile remove [find name={name}]",
        )

    async def create_hotspot(self, name, interface, pool, profile):
        """Cria a instância do hotspot."""
        await self.safe_add(
            "/ip hotspot",
            f"name={name}",
            f"/ip hotspot add name={name} interface={interface} "
            f"address-pool={pool} profile={profile} disabled=no",
            f"/ip hotspot remove [find name={name}]",
        )

    async def create_nat(self, out_interface):
        """Cria regra NAT masquerade para a WAN."""
        await self.safe_add(
            "/ip firewall nat",
            f"chain=srcnat out-interface={out_interface} action=masquerade",
            f"/ip firewall nat add chain=srcnat out-interface={out_interface} "
            f'action=masquerade comment="NAT-HOTSPOT"',
            f"/ip firewall nat remove [find out-interface={out_interface} chain=srcnat]",
        )

    async def create_user(self, username, password, server="all"):
        """Cria um usuário no hotspot."""
        await self.safe_add(
            "/ip hotspot user",
            f'name="{username}"',
            f'/ip hotspot user add name="{username}" password="{password}" server={server}',
            f'/ip hotspot user remove [find name="{username}"]',
        )

    async def create_user_profile(self, name, idle_timeout="none", keepalive_timeout="2m", 
                              status_autorefresh="1m", shared_users=1, add_mac_cookie="yes",
                              mac_cookie_timeout="3d", address_list="", rate_limit=""):
        """
        Cria um perfil de usuário hotspot (/ip hotspot user profile).
        
        Parâmetros:
        - name: Nome do perfil (obrigatório)
        - idle_timeout: Tempo de inatividade antes de desconectar (ex: "5m", "none")
        - keepalive_timeout: Tempo de verificação de conexão (ex: "2m")
        - status_autorefresh: Intervalo de atualização da página de status (ex: "1m")
        - shared_users: Número de dispositivos simultâneos (padrão: 1)
        - add_mac_cookie: Habilita cookie MAC (yes/no)
        - mac_cookie_timeout: Validade do cookie MAC (ex: "3d")
        - address_list: Lista de endereços para firewall/QoS
        - rate_limit: Limite de banda (ex: "10M/5M" para download/upload)
        """
        # Monta o comando base com nome
        cmd = f'/ip hotspot user profile add name="{name}"'
        
        # Adiciona parâmetros
        if idle_timeout:
            cmd += f' idle-timeout={idle_timeout}'
        
        if keepalive_timeout:
            cmd += f' keepalive-timeout={keepalive_timeout}'
        
        if status_autorefresh:
            cmd += f' status-autorefresh={status_autorefresh}'
        
        cmd += f' shared-users={shared_users}'
        cmd += f' add-mac-cookie={add_mac_cookie}'
        
        if mac_cookie_timeout:
            cmd += f' mac-cookie-timeout={mac_cookie_timeout}'
        
        if address_list:
            cmd += f' address-list={address_list}'
        
        # Adiciona rate-limit se especificado
        if rate_limit:
            cmd += f' rate-limit="{rate_limit}"'
        
        # Comando de rollback (remove o perfil)
        rollback_cmd = f'/ip hotspot user profile remove [find name="{name}"]'
        
        # Verifica se já existe e cria
        await self.safe_add(
            "/ip hotspot user profile",
            f'name="{name}"',
            cmd,
            rollback_cmd,
        )

    async def create_user_with_profile(self, username, password, profile_name, server="all"):
        """
        Cria um usuário hotspot associado a um perfil específico.
        
        Parâmetros:
        - username: Nome do usuário
        - password: Senha do usuário
        - profile_name: Nome do perfil a ser usado
        - server: Servidor hotspot (ex: "all", "hotspot1")
        """
        cmd = f'/ip hotspot user add name="{username}" password="{password}"'
        
        if profile_name:
            cmd += f' profile="{profile_name}"'
        
        if server:
            cmd += f' server={server}'
        
        rollback_cmd = f'/ip hotspot user remove [find name="{username}"]'
        
        await self.safe_add(
            "/ip hotspot user",
            f'name="{username}"',
            cmd,
            rollback_cmd,
        )

    async def add_bypass_mac(self, mac, server, comment=""):
        """Adiciona um MAC address como bypassed no hotspot."""
        comment_part = f' comment="{comment}"' if comment else ""
        await self.safe_add(
            "/ip hotspot ip-binding",
            f"mac-address={mac}",
            f"/ip hotspot ip-binding add mac-address={mac} server={server} type=bypassed{comment_part}",
            f"/ip hotspot ip-binding remove [find mac-address={mac}]",
        )

    async def add_walled_garden_ip(self, dst_address, dst_port=None, protocol="tcp", comment=""):
        """Adiciona uma entrada no walled-garden IP (acesso sem autenticação)."""
        port_part = f" dst-port={dst_port}" if dst_port else ""
        comment_part = f' comment="{comment}"' if comment else ""
        where = f"dst-address={dst_address}"

        await self.safe_add(
            "/ip hotspot walled-garden ip",
            where,
            f"/ip hotspot walled-garden ip add action=accept dst-address={dst_address} "
            f"protocol={protocol}{port_part}{comment_part} disabled=no",
            f"/ip hotspot walled-garden ip remove [find dst-address={dst_address}]",
        )

    # =========================================================================
    # REMOÇÃO COMPLETA DO HOTSPOT
    # =========================================================================

    async def teardown_hotspot(self, config):
        """
        Remove completamente o hotspot e todos os recursos associados.
        Ordem inversa à criação para evitar dependências.
        """
        print("🗑️  Removendo hotspot...")

        name = config.get("hotspot", "hotspot1")
        bridge = config.get("bridge", "bridge2")
        pool = config.get("pool", "hs-pool-20")
        dhcp = config.get("dhcp", "dhcp2")
        profile = config.get("profile", "hsprof1")
        ip = config.get("ip", "")
        network = config.get("network", "")
        wan = config.get("wan", "ether1")
        lan_interfaces = config.get("lan_interfaces", [config.get("lan", "")])
        bypass_macs = config.get("bypass_macs", [])
        users = config.get("users", [])
        user_profiles = config.get("user_profiles", [])

        # Usuários
        for user in users:
            if user:
                await self.safe_remove(f'/ip hotspot user remove [find name="{user}"]')

        # Perfis de usuário
        for profile_name in user_profiles:
            if profile_name:
                await self.safe_remove(f'/ip hotspot user profile remove [find name="{profile_name}"]')

        # Bypass MACs
        for mac in bypass_macs:
            await self.safe_remove(f"/ip hotspot ip-binding remove [find mac-address={mac}]")

        # Hotspot
        await self.safe_remove(f"/ip hotspot remove [find name={name}]")

        # Perfil do hotspot
        await self.safe_remove(f"/ip hotspot profile remove [find name={profile}]")

        # DHCP
        await self.safe_remove(f"/ip dhcp-server remove [find name={dhcp}]")

        # Rede DHCP
        if network:
            await self.safe_remove(f"/ip dhcp-server network remove [find address={network}]")

        # IP da bridge
        if ip:
            ip_addr = ip.split("/")[0]
            await self.safe_remove(f'/ip address remove [find address~"{ip_addr}"]')

        # Pool
        await self.safe_remove(f"/ip pool remove [find name={pool}]")

        # NAT
        await self.safe_remove(
            f"/ip firewall nat remove [find out-interface={wan} chain=srcnat action=masquerade]"
        )

        # Ports da bridge
        for iface in lan_interfaces:
            if iface:
                await self.safe_remove(
                    f"/interface bridge port remove [find bridge={bridge} interface={iface}]"
                )

        # Bridge
        await self.safe_remove(f"/interface bridge remove [find name={bridge}]")

        print("✅ Hotspot removido com sucesso")

    # =========================================================================
    # ORQUESTRAÇÃO PRINCIPAL
    # =========================================================================

    async def setup_hotspot(self, config):
        """
        Provisiona o hotspot completo na ordem correta.

        Config esperado:
        {
            "bridge":        str   - nome da bridge (ex: "bridge2")
            "lan":           str   - interface LAN principal (ex: "ether2")
            "lan_extras":    list  - interfaces LAN adicionais (opcional)
            "pool":          str   - nome do pool (ex: "hs-pool-20")
            "ranges":        str   - range de IPs (ex: "192.168.0.2-192.168.3.254")
            "dhcp":          str   - nome do DHCP server (ex: "dhcp2")
            "lease_time":    str   - tempo de lease (padrão: "1h")
            "profile":       str   - nome do perfil hotspot (ex: "hsprof1")
            "hotspot":       str   - nome do hotspot (ex: "hotspot1")
            "ip":            str   - IP/máscara da bridge (ex: "192.168.1.1/22")
            "network":       str   - rede (ex: "192.168.0.0/22")
            "gateway":       str   - gateway (ex: "192.168.1.1")
            "wan":           str   - interface WAN para NAT (ex: "ether1")
            "user":          str   - usuário hotspot (ex: "admin") [opcional]
            "password":      str   - senha do usuário [opcional]
            "user_profile":  dict  - perfil de usuário hotspot (opcional)
            "users_with_profiles": list - lista de usuários com perfis específicos (opcional)
            "bypass_macs":   list  - MACs liberados sem login (opcional)
            "walled_garden": list  - dicts com {dst_address, dst_port, comment} (opcional)
            "dns_name":      str   - DNS name do hotspot (opcional)
        }
        """
        self.rollback_stack.clear()

        try:
            # 1. Valida pacote hotspot
            await self.ensure_hotspot_package()

            # 2. Valida interfaces antes de qualquer criação
            await self.ensure_interface_exists(config["lan"])
            for extra in config.get("lan_extras", []):
                await self.ensure_interface_exists(extra)
            await self.ensure_interface_exists(config["wan"])

            # 3. Garante acesso SSH/Winbox após hotspot subir
            await self.ensure_management_access()

            # 4. Bridge
            await self.create_bridge(config["bridge"])

            # 5. Adiciona interfaces LAN à bridge
            await self.add_interface_to_bridge(config["bridge"], config["lan"])
            for extra in config.get("lan_extras", []):
                await self.add_interface_to_bridge(config["bridge"], extra)

            # 6. IP da bridge (deve vir antes do DHCP e hotspot)
            gateway = config["gateway"]
            network_cidr = config["network"]
            await self.assign_ip(config["bridge"], config["ip"], network_cidr.split("/")[0])

            # 7. Pool de IPs
            await self.create_pool(config["pool"], config["ranges"])

            # 8. Rede e servidor DHCP
            await self.create_dhcp_network(network_cidr, gateway)
            await self.create_dhcp(
                config["dhcp"],
                config["bridge"],
                config["pool"],
                config.get("lease_time", "1h"),
            )

            # 9. Perfil e instância do hotspot
            await self.create_hotspot_profile(
                config["profile"],
                gateway,
                config.get("dns_name", ""),
            )
            await self.create_hotspot(
                config["hotspot"],
                config["bridge"],
                config["pool"],
                config["profile"],
            )

            # 10. NAT para WAN
            await self.create_nat(config["wan"])

            # 11. Cria perfis de usuário hotspot (se especificado)
            if "user_profile" in config:
                profile = config["user_profile"]
                await self.create_user_profile(
                    name=profile["name"],
                    idle_timeout=profile.get("idle_timeout", "none"),
                    keepalive_timeout=profile.get("keepalive_timeout", "2m"),
                    status_autorefresh=profile.get("status_autorefresh", "1m"),
                    shared_users=profile.get("shared_users", 1),
                    add_mac_cookie=profile.get("add_mac_cookie", "yes"),
                    mac_cookie_timeout=profile.get("mac_cookie_timeout", "3d"),
                    address_list=profile.get("address_list", ""),
                    rate_limit=profile.get("rate_limit", "") 
                )

            # 12. Cria usuários com perfis específicos
            for user in config.get("users_with_profiles", []):
                await self.create_user_with_profile(
                    username=user["username"],
                    password=user["password"],
                    profile_name=user.get("profile_name", ""),
                    server=user.get("server", "all")
                )

            # 13. Bypass MACs
            for mac in config.get("bypass_macs", []):
                comment = ""
                if isinstance(mac, dict):
                    comment = mac.get("comment", "")
                    mac = mac["mac"]
                await self.add_bypass_mac(mac, config["hotspot"], comment)

            # 14. Walled Garden
            for wg in config.get("walled_garden", []):
                await self.add_walled_garden_ip(
                    wg["dst_address"],
                    wg.get("dst_port"),
                    wg.get("protocol", "tcp"),
                    wg.get("comment", ""),
                )

            # 15. Usuário padrão (se não criado via users_with_profiles)
            if "user" in config and "password" in config:
                # Verifica se o usuário padrão já foi criado
                user_exists = False
                for user in config.get("users_with_profiles", []):
                    if user.get("username") == config["user"]:
                        user_exists = True
                        break
                
                if not user_exists:
                    await self.create_user(
                        config["user"],
                        config["password"],
                        config.get("user_server", "all"),
                    )

            print("✅ Hotspot provisionado com sucesso")

        except Exception as e:
            print(f"❌ Erro durante provisionamento: {e}")
            await self.rollback()
            raise

    # =========================================================================
    # DIAGNÓSTICO
    # =========================================================================

    async def diagnostics(self):
        """
        Retorna um dict com o estado atual do roteador.
        Útil para validar o provisionamento.
        """
        sections = {
            "identity":          "/system identity print",
            "packages":          "/system package print",
            "interfaces":        "/interface print",
            "bridge_ports":      "/interface bridge port print",
            "ip_addresses":      "/ip address print",
            "pools":             "/ip pool print",
            "dhcp_servers":      "/ip dhcp-server print",
            "dhcp_networks":     "/ip dhcp-server network print",
            "hotspot":           "/ip hotspot print",
            "hotspot_prof":      "/ip hotspot profile print",
            "hs_user_profiles":  "/ip hotspot user profile print",
            "hs_users":          "/ip hotspot user print",
            "hs_bindings":       "/ip hotspot ip-binding print",
            "hs_walled":         "/ip hotspot walled-garden ip print",
            "nat_rules":         "/ip firewall nat print",
            "filter_rules":      "/ip firewall filter print",
        }

        result = {}
        for key, cmd in sections.items():
            try:
                result[key] = await self.exec(cmd)
            except Exception as e:
                result[key] = f"ERRO: {e}"

        return result

    async def print_diagnostics(self):
        """Imprime diagnóstico formatado no terminal."""
        data = await self.diagnostics()
        labels = {
            "identity":          "📌 Identity",
            "packages":          "📦 Pacotes",
            "interfaces":        "📡 Interfaces",
            "bridge_ports":      "🔗 Bridge Ports",
            "ip_addresses":      "🌐 IP Addresses",
            "pools":             "🎱 Pools",
            "dhcp_servers":      "📋 DHCP Servers",
            "dhcp_networks":     "🗺️  DHCP Networks",
            "hotspot":           "🔥 Hotspot",
            "hotspot_prof":      "⚙️  Hotspot Profiles",
            "hs_user_profiles":  "👥 User Profiles",
            "hs_users":          "👤 Usuários",
            "hs_bindings":       "🔓 IP Bindings",
            "hs_walled":         "🌿 Walled Garden",
            "nat_rules":         "🔄 NAT Rules",
            "filter_rules":      "🛡️  Firewall Filter",
        }
        for key, label in labels.items():
            print(f"\n{label}:")
            print(data.get(key, "(vazio)") or "(vazio)")
            
    # =========================================================================
    # GERENCIAMENTO DE USUÁRIOS (BLOQUEIO/DESBLOQUEIO)
    # =========================================================================
    # =========================================================================
    # HELPERS
    # =========================================================================

    async def _build_where(self, field, value, server="all"):
        where = f'where {field}="{value}"'
        if server != "all":
            where += f' and server="{server}"'
        return where


    async def ensure_profile(self, rate_limit):
        """
        Garante que exista um profile com rate-limit
        """
        profile_name = f"profile_{rate_limit.replace('/', '_')}"

        try:
            cmd = f'/ip hotspot user profile add name="{profile_name}" rate-limit="{rate_limit}"'
            await self.exec(cmd)
        except:
            pass  # já existe

        return profile_name


    # =========================================================================
    # GERENCIAMENTO DE USUÁRIOS
    # =========================================================================

    async def disable_hotspot_user(self, username, server="all"):
        try:
            where = await self._build_where("name", username, server)
            cmd = f'/ip hotspot user disable [find {where}]'
            await self.exec(cmd)
            return True

        except Exception as e:
            print(f"Erro ao desabilitar usuário {username}: {e}")
            return False


    async def enable_hotspot_user(self, username, server="all"):
        try:
            where = await self._build_where("name", username, server)
            cmd = f'/ip hotspot user enable [find {where}]'
            await self.exec(cmd)
            return True

        except Exception as e:
            print(f"Erro ao habilitar usuário {username}: {e}")
            return False


    async def create_hotspot_user(self, username, password, server="all", profile=None):
        try:
            cmd = f'/ip hotspot user add name="{username}" password="{password}" server="{server}"'
            if profile:
                cmd += f' profile="{profile}"'

            await self.exec(cmd)
            return True

        except Exception as e:
            print(f"Erro ao criar usuário {username}: {e}")
            return False


    # =========================================================================
    # LIMPEZA / SESSÕES
    # =========================================================================

    async def remove_hotspot_cookie(self, username, server="all"):
        try:
            where = await self._build_where("user", username, server)
            cmd = f'/ip hotspot cookie remove [find {where}]'
            await self.exec(cmd)
            return True

        except Exception as e:
            print(f"Erro ao remover cookie do usuário {username}: {e}")
            return False


    async def remove_hotspot_host(self, username, server="all"):
        try:
            where = await self._build_where("user", username, server)
            cmd = f'/ip hotspot host remove [find {where}]'
            await self.exec(cmd)
            return True

        except Exception as e:
            print(f"Erro ao remover host do usuário {username}: {e}")
            return False


    async def remove_hotspot_active(self, username, server="all"):
        try:
            where = await self._build_where("user", username, server)
            cmd = f'/ip hotspot active remove [find {where}]'
            await self.exec(cmd)
            return True

        except Exception as e:
            print(f"Erro ao remover sessão ativa do usuário {username}: {e}")
            return False


    async def remove_hotspot_ip_binding(self, username, server="all"):
        try:
            where = f'where comment="{username}"'
            cmd = f'/ip hotspot ip-binding remove [find {where}]'
            await self.exec(cmd)
            return True

        except Exception as e:
            print(f"Erro ao remover IP binding do usuário {username}: {e}")
            return False


    # =========================================================================
    # RATE LIMIT (CORRETO VIA PROFILE)
    # =========================================================================

    async def set_user_rate_limit(self, username, rate_limit, server="all"):
        """
        Aplica rate-limit via profile (forma correta no hotspot)
        """
        try:
            profile = await self.ensure_profile(rate_limit)
            where = await self._build_where("name", username, server)

            cmd = f'/ip hotspot user set [find {where}] profile="{profile}"'
            await self.exec(cmd)

            return True

        except Exception as e:
            print(f"Erro ao aplicar rate-limit no usuário {username}: {e}")
            return False


    # =========================================================================
    # FLUXOS COMPLETOS
    # =========================================================================

    async def full_disconnect_hotspot_user(self, username, server="all"):
        try:
            await self.remove_hotspot_active(username, server)
            await self.remove_hotspot_cookie(username, server)
            await self.remove_hotspot_host(username, server)
            await self.disable_hotspot_user(username, server)

            return True

        except Exception as e:
            print(f"Erro ao desconectar usuário {username}: {e}")
            return False


    async def full_unblock_hotspot_user(
        self,
        username,
        password,
        server="all",
        profile=None,
        rate_limit=None
    ):
        try:
            await self.enable_hotspot_user(username, server)

            if not await self.exists("/ip hotspot user", f'name="{username}"'):
                await self.create_hotspot_user(username, password, server, profile)

            if rate_limit:
                await self.set_user_rate_limit(username, rate_limit, server)

            return True

        except Exception as e:
            print(f"Erro ao desbloquear usuário {username}: {e}")
            return False