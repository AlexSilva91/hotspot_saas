# app/services/mikrotik_ssh_service.py

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

        ignored_patterns = ["no such item"]
        if any(p in full for p in ignored_patterns):
            return out

        error_patterns = [
            "failure", "bad command", "syntax error", "no such command",
            "invalid value", "already have such", "expected end of command",
            "ambiguous value",
        ]
        if any(e in full for e in error_patterns):
            raise Exception(f"Erro no comando [{command}]: {out or err}")

        return out

    async def exec_silent(self, command):
        """Executa comando ignorando qualquer erro."""
        try:
            return await self.exec(command)
        except Exception:
            return ""

    # =========================================================================
    # HELPERS
    # =========================================================================

    async def exists(self, path, where):
        """Verifica se um recurso existe no RouterOS."""
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
        """Adiciona um recurso somente se ele ainda não existir."""
        if await self.exists(path, where):
            return

        await self.exec(command)
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
        """Desfaz todas as operações registradas na pilha."""
        for cmd in reversed(self.rollback_stack):
            await self.safe_remove(cmd)
        self.rollback_stack.clear()

    # =========================================================================
    # VALIDAÇÕES
    # =========================================================================

    async def ensure_hotspot_package(self):
        """Garante que o pacote hotspot está instalado e ativo."""
        packages = await self.exec("/system package print")
        if "hotspot" not in packages.lower():
            raise Exception(
                "Pacote 'hotspot' não está instalado neste RouterOS."
            )

    async def ensure_interface_exists(self, name):
        """Garante que uma interface existe no roteador."""
        if not await self.exists("/interface", f"name={name}"):
            raise Exception(f"Interface '{name}' não encontrada.")

    async def ensure_management_access(self):
        """Garante que SSH e Winbox continuem acessíveis após o hotspot subir."""
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
        """Cria um perfil de usuário hotspot."""
        cmd = f'/ip hotspot user profile add name="{name}"'
        
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
        if rate_limit:
            cmd += f' rate-limit="{rate_limit}"'
        
        rollback_cmd = f'/ip hotspot user profile remove [find name="{name}"]'
        
        await self.safe_add(
            "/ip hotspot user profile",
            f'name="{name}"',
            cmd,
            rollback_cmd,
        )

    async def create_user_with_profile(self, username, password, profile_name, server="all"):
        """Cria um usuário hotspot associado a um perfil específico."""
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
        cmd = f'/ip hotspot ip-binding add mac-address={mac} server={server} type=bypassed{comment_part}'
        await self.conn.run(cmd)
    
    async def disable_bypass_mac(self, mac):
        """Desativa um ip-binding."""
        await self.exec(
            f"/ip hotspot ip-binding set [find mac-address={mac}] type=blocked disabled=yes"
        )

    async def enable_bypass_mac(self, mac):
        """Ativa um ip-binding."""
        await self.exec(
            f"/ip hotspot ip-binding set [find mac-address={mac}] type=regular disabled=no"
        )

    async def set_binding_type(self, mac, binding_type):
        """Muda o type de um ip-binding existente."""
        if binding_type not in ("blocked", "bypassed", "regular"):
            raise Exception(f"Type inválido: {binding_type}")

        await self.exec(
            f"/ip hotspot ip-binding set [find mac-address={mac}] type={binding_type}"
        )
    
    async def add_walled_garden_ip(self, dst_address, dst_port=None, protocol="tcp", comment=""):
        """Adiciona uma entrada no walled-garden IP."""
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
    # ORQUESTRAÇÃO PRINCIPAL
    # =========================================================================

    async def setup_hotspot(self, config):
        """
        Provisiona o hotspot completo.
        
        Args:
            config: Dicionário com configurações do hotspot
        """
        self.rollback_stack.clear()

        try:
            await self.ensure_hotspot_package()
            await self.ensure_interface_exists(config["lan"])
            for extra in config.get("lan_extras", []):
                await self.ensure_interface_exists(extra)
            await self.ensure_interface_exists(config["wan"])
            await self.ensure_management_access()

            await self.create_bridge(config["bridge"])
            await self.add_interface_to_bridge(config["bridge"], config["lan"])
            for extra in config.get("lan_extras", []):
                await self.add_interface_to_bridge(config["bridge"], extra)

            gateway = config["gateway"]
            network_cidr = config["network"]
            await self.assign_ip(config["bridge"], config["ip"], network_cidr.split("/")[0])
            await self.create_pool(config["pool"], config["ranges"])
            await self.create_dhcp_network(network_cidr, gateway)
            await self.create_dhcp(
                config["dhcp"],
                config["bridge"],
                config["pool"],
                config.get("lease_time", "1h"),
            )
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
            await self.create_nat(config["wan"])

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

            users_created = []
            for user in config.get("users_with_profiles", []):
                await self.create_user_with_profile(
                    username=user["username"],
                    password=user["password"],
                    profile_name=user.get("profile_name", ""),
                    server=user.get("server", "all")
                )
                users_created.append(user["username"])

            bypass_macs_list = []
            for mac in config.get("bypass_macs", []):
                comment = ""
                if isinstance(mac, dict):
                    comment = mac.get("comment", "")
                    mac_addr = mac["mac"]
                else:
                    mac_addr = mac
                bypass_macs_list.append(mac_addr)
                await self.add_bypass_mac(mac_addr, config["hotspot"], comment)

            for wg in config.get("walled_garden", []):
                await self.add_walled_garden_ip(
                    wg["dst_address"],
                    wg.get("dst_port"),
                    wg.get("protocol", "tcp"),
                    wg.get("comment", ""),
                )

            if "user" in config and "password" in config:
                if config["user"] not in users_created:
                    await self.create_user(
                        config["user"],
                        config["password"],
                        config.get("user_server", "all"),
                    )
                    users_created.append(config["user"])

            config["users"] = users_created
            config["user_profiles"] = [p["name"] for p in config.get("user_profile", [])] if "user_profile" in config else []
            config["bypass_macs"] = bypass_macs_list
            config["lan_interfaces"] = [config["lan"]] + config.get("lan_extras", [])

        except Exception as e:
            await self.rollback()
            raise

    async def teardown_hotspot(self, config):
        """
        Remove completamente o hotspot e todos os recursos associados.
        
        Args:
            config: Dicionário com configurações do hotspot a ser removido
        """
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
        
        default_user = config.get("user")
        if default_user and default_user not in users:
            users.append(default_user)
        
        for user in users:
            if user:
                await self.safe_remove(f'/ip hotspot user remove [find name="{user}"]')
                await self.safe_remove(f'/ip hotspot user remove [find name="{user}" server={name}]')
                await self.safe_remove(f'/ip hotspot user remove [find name="{user}" server=all]')

        for profile_name in user_profiles:
            if profile_name:
                await self.safe_remove(f'/ip hotspot user profile remove [find name="{profile_name}"]')

        for mac in bypass_macs:
            if isinstance(mac, dict):
                mac = mac.get("mac", mac)
            if mac:
                await self.safe_remove(f"/ip hotspot ip-binding remove [find mac-address={mac}]")

        await self.safe_remove(f"/ip hotspot remove [find name={name}]")
        await self.safe_remove(f"/ip hotspot remove [find where name~'hotspot']")
        await self.safe_remove(f"/ip hotspot profile remove [find name={profile}]")
        await self.safe_remove(f"/ip hotspot profile remove [find where name~'hsprof']")
        await self.safe_remove(f"/ip dhcp-server remove [find name={dhcp}]")
        await self.safe_remove(f"/ip dhcp-server remove [find where interface={bridge}]")
        
        if network:
            await self.safe_remove(f"/ip dhcp-server network remove [find address={network}]")
            await self.safe_remove(f'/ip dhcp-server network remove [find comment="hotspot network"]')
        
        gateway = config.get("gateway", "")
        if gateway:
            await self.safe_remove(f"/ip dhcp-server network remove [find gateway={gateway}]")

        if ip:
            ip_addr = ip.split("/")[0]
            await self.safe_remove(f'/ip address remove [find address~"{ip_addr}"]')
            await self.safe_remove(f'/ip address remove [find interface={bridge}]')

        await self.safe_remove(f"/ip pool remove [find name={pool}]")
        await self.safe_remove(f"/ip pool remove [find where name~'hs-pool']")
        await self.safe_remove(
            f"/ip firewall nat remove [find out-interface={wan} chain=srcnat action=masquerade]"
        )
        await self.safe_remove(f'/ip firewall nat remove [find comment="NAT-HOTSPOT"]')
        await self.safe_remove(f"/ip firewall nat remove [find out-interface={bridge} chain=srcnat]")
        await self.safe_remove(f'/ip firewall filter remove [find chain="unused-hs-chain"]')
        await self.safe_remove(f'/ip firewall nat remove [find chain="unused-hs-chain"]')

        for iface in lan_interfaces:
            if iface:
                await self.safe_remove(
                    f"/interface bridge port remove [find bridge={bridge} interface={iface}]"
                )
        await self.safe_remove(f"/interface bridge port remove [find bridge={bridge}]")
        await self.safe_remove(f"/interface bridge remove [find name={bridge}]")
        await self.safe_remove(f'/ip firewall filter remove [find comment="MGMT_SAFE"]')

    # =========================================================================
    # DIAGNÓSTICO
    # =========================================================================

    async def diagnostics(self):
        """Retorna um dict com o estado atual do roteador."""
        sections = {
            "identity": "/system identity print",
            "packages": "/system package print",
            "interfaces": "/interface print",
            "bridge_ports": "/interface bridge port print",
            "ip_addresses": "/ip address print",
            "pools": "/ip pool print",
            "dhcp_servers": "/ip dhcp-server print",
            "dhcp_networks": "/ip dhcp-server network print",
            "hotspot": "/ip hotspot print",
            "hotspot_prof": "/ip hotspot profile print",
            "hs_user_profiles": "/ip hotspot user profile print",
            "hs_users": "/ip hotspot user print",
            "hs_bindings": "/ip hotspot ip-binding print",
            "hs_walled": "/ip hotspot walled-garden ip print",
            "nat_rules": "/ip firewall nat print",
            "filter_rules": "/ip firewall filter print",
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
            "identity": "📌 Identity",
            "packages": "📦 Pacotes",
            "interfaces": "📡 Interfaces",
            "bridge_ports": "🔗 Bridge Ports",
            "ip_addresses": "🌐 IP Addresses",
            "pools": "🎱 Pools",
            "dhcp_servers": "📋 DHCP Servers",
            "dhcp_networks": "🗺️ DHCP Networks",
            "hotspot": "🔥 Hotspot",
            "hotspot_prof": "⚙️ Hotspot Profiles",
            "hs_user_profiles": "👥 User Profiles",
            "hs_users": "👤 Usuários",
            "hs_bindings": "🔓 IP Bindings",
            "hs_walled": "🌿 Walled Garden",
            "nat_rules": "🔄 NAT Rules",
            "filter_rules": "🛡️ Firewall Filter",
        }
        for key, label in labels.items():
            print(f"\n{label}:")
            print(data.get(key, "(vazio)") or "(vazio)")
            
    # =========================================================================
    # GERENCIAMENTO DE USUÁRIOS
    # =========================================================================

    async def _build_where(self, field, value, server="all"):
        """Constrói condição WHERE para comandos."""
        where = f'where {field}="{value}"'
        if server != "all":
            where += f' and server="{server}"'
        return where

    async def ensure_profile(self, rate_limit):
        """Garante que exista um profile com rate-limit."""
        profile_name = f"profile_{rate_limit.replace('/', '_')}"
        try:
            cmd = f'/ip hotspot user profile add name="{profile_name}" rate-limit="{rate_limit}"'
            await self.exec(cmd)
        except:
            pass
        return profile_name

    async def disable_hotspot_user(self, username, server="all"):
        """Desabilita um usuário hotspot."""
        try:
            where = await self._build_where("name", username, server)
            cmd = f'/ip hotspot user disable [find {where}]'
            await self.exec(cmd)
            return True
        except Exception as e:
            return False

    async def enable_hotspot_user(self, username, server="all"):
        """Habilita um usuário hotspot."""
        try:
            where = await self._build_where("name", username, server)
            cmd = f'/ip hotspot user enable [find {where}]'
            await self.exec(cmd)
            return True
        except Exception as e:
            return False

    async def create_hotspot_user(self, username, password, server="all", profile=None):
        """Cria um usuário hotspot."""
        try:
            cmd = f'/ip hotspot user add name="{username}" password="{password}" server="{server}"'
            if profile:
                cmd += f' profile="{profile}"'
            await self.exec(cmd)
            return True
        except Exception as e:
            return False

    async def remove_hotspot_cookie(self, username, server="all"):
        """Remove cookies de um usuário."""
        try:
            where = await self._build_where("user", username, server)
            cmd = f'/ip hotspot cookie remove [find {where}]'
            await self.exec(cmd)
            return True
        except Exception as e:
            return False

    async def remove_hotspot_host(self, username, server="all"):
        """Remove hosts de um usuário."""
        try:
            where = await self._build_where("user", username, server)
            cmd = f'/ip hotspot host remove [find {where}]'
            await self.exec(cmd)
            return True
        except Exception as e:
            return False

    async def remove_hotspot_active(self, username, server="all"):
        """Remove sessões ativas de um usuário."""
        try:
            where = await self._build_where("user", username, server)
            cmd = f'/ip hotspot active remove [find {where}]'
            await self.exec(cmd)
            return True
        except Exception as e:
            return False

    async def remove_hotspot_ip_binding(self, username, server="all"):
        """Remove IP bindings de um usuário."""
        try:
            where = f'where comment="{username}"'
            cmd = f'/ip hotspot ip-binding remove [find {where}]'
            await self.exec(cmd)
            return True
        except Exception as e:
            return False

    async def set_user_rate_limit(self, username, rate_limit, server="all"):
        """Aplica rate-limit via profile."""
        try:
            profile = await self.ensure_profile(rate_limit)
            where = await self._build_where("name", username, server)
            cmd = f'/ip hotspot user set [find {where}] profile="{profile}"'
            await self.exec(cmd)
            return True
        except Exception as e:
            return False

    async def full_disconnect_hotspot_user(self, username, server="all"):
        """Desconecta completamente um usuário."""
        try:
            await self.remove_hotspot_active(username, server)
            await self.remove_hotspot_cookie(username, server)
            await self.remove_hotspot_host(username, server)
            await self.disable_hotspot_user(username, server)
            return True
        except Exception as e:
            return False

    async def full_unblock_hotspot_user(self, username, password, server="all", profile=None, rate_limit=None):
        """Desbloqueia completamente um usuário."""
        try:
            await self.enable_hotspot_user(username, server)
            if not await self.exists("/ip hotspot user", f'name="{username}"'):
                await self.create_hotspot_user(username, password, server, profile)
            if rate_limit:
                await self.set_user_rate_limit(username, rate_limit, server)
            return True
        except Exception as e:
            return False