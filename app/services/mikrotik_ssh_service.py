import paramiko
import ipaddress


class MikroTikSSHService:
    def __init__(self, host, username, password, port=22, timeout=10):
        self.host = host
        self.username = username
        self.password = password
        self.port = port
        self.timeout = timeout
        self.client = None

    # =============================
    # CONEXÃO (COMPATÍVEL COM MK)
    # =============================
    def connect(self):
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        transport = paramiko.Transport((self.host, self.port))
        security = transport.get_security_options()

        security.kex = [
            'diffie-hellman-group14-sha1',
            'diffie-hellman-group1-sha1'
        ]
        security.key_types = ['ssh-rsa']
        security.ciphers = [
            'aes128-ctr',
            'aes192-ctr',
            'aes256-ctr'
        ]

        transport.connect(
            username=self.username,
            password=self.password
        )

        self.client._transport = transport

    def close(self):
        if self.client:
            self.client.close()

    # =============================
    # EXECUÇÃO
    # =============================
    def exec(self, command):
        stdin, stdout, stderr = self.client.exec_command(command)

        out = stdout.read().decode()
        err = stderr.read().decode()

        if "failure" in out.lower() or "failure" in err.lower():
            raise Exception(f"Erro MikroTik: {out or err}")

        return out.strip()

    # =============================
    # HELPERS
    # =============================
    def exists(self, path, where):
        return bool(self.exec(f"{path} print where {where}"))

    def remove(self, path, where):
        self.exec(f"{path} remove [find {where}]")

    # =============================
    # GARANTE ACESSO (SSH + WINBOX)
    # =============================
    def ensure_management_access(self):
        rules = [
            ("input", 22),
            ("input", 8291),
            ("hs-input", 22),
            ("hs-input", 8291),
        ]

        for chain, port in rules:
            where = f"chain={chain} protocol=tcp dst-port={port}"

            if not self.exists("/ip firewall filter", where):
                self.exec(
                    f"/ip firewall filter add chain={chain} "
                    f"protocol=tcp dst-port={port} action=accept place-before=0"
                )

    # =============================
    # GARANTE INTERFACE VÁLIDA
    # =============================
    def ensure_interface(self, interface):
        if not self.exists("/interface", f"name={interface}"):
            raise Exception(f"Interface {interface} não existe")

    # =============================
    # REMOVE DHCP NETWORK DUPLICADO
    # =============================
    def cleanup_dhcp_network(self, network):
        if self.exists("/ip dhcp-server network", f"address={network}"):
            self.remove("/ip dhcp-server network", f"address={network}")

    # =============================
    # HOTSPOT COMPLETO
    # =============================
    def create_hotspot(self, interface, network_cidr, name_prefix="hs"):
        self.ensure_management_access()
        self.ensure_interface(interface)

        net = ipaddress.ip_network(network_cidr, strict=False)
        hosts = list(net.hosts())

        if len(hosts) < 10:
            raise Exception("Rede muito pequena")

        gateway = str(hosts[0])
        pool_start = str(hosts[1])
        pool_end = str(hosts[-1])

        pool = f"{name_prefix}_pool_{interface}"
        profile = f"{name_prefix}_profile_{interface}"
        hotspot = f"{name_prefix}_{interface}"
        dhcp = f"{name_prefix}_dhcp_{interface}"

        dns_name = f"{name_prefix}.local"

        # =============================
        # LIMPEZA
        # =============================
        if self.exists("/ip hotspot", f"name={hotspot}"):
            self.remove("/ip hotspot", f"name={hotspot}")

        if self.exists("/ip hotspot profile", f"name={profile}"):
            self.remove("/ip hotspot profile", f"name={profile}")

        if self.exists("/ip dhcp-server", f"name={dhcp}"):
            self.remove("/ip dhcp-server", f"name={dhcp}")

        if self.exists("/ip pool", f"name={pool}"):
            self.remove("/ip pool", f"name={pool}")

        if self.exists("/ip address", f"address~\"{gateway}\""):
            self.remove("/ip address", f"address~\"{gateway}\"")

        self.cleanup_dhcp_network(str(net))

        # =============================
        # CRIAÇÃO
        # =============================
        self.exec(f"/ip address add address={gateway}/{net.prefixlen} interface={interface}")

        self.exec(f"/ip pool add name={pool} ranges={pool_start}-{pool_end}")

        self.exec(
            f"/ip dhcp-server add name={dhcp} interface={interface} "
            f"address-pool={pool} disabled=no"
        )

        self.exec(
            f"/ip dhcp-server network add address={net} "
            f"gateway={gateway} dns-server=8.8.8.8"
        )

        # NAT CORRETO (usa saída WAN = ether1)
        self.exec(
            f"/ip firewall nat add chain=srcnat out-interface=ether1 action=masquerade"
        )

        self.exec(
            f"/ip hotspot profile add name={profile} "
            f"hotspot-address={gateway} dns-name={dns_name}"
        )

        self.exec(
            f"/ip hotspot add name={hotspot} interface={interface} "
            f"address-pool={pool} profile={profile} disabled=no"
        )

        # =============================
        # VALIDAÇÃO
        # =============================
        if not self.exists("/ip hotspot", f"name={hotspot}"):
            raise Exception("Hotspot não foi criado")

        return {
            "hotspot": hotspot,
            "interface": interface,
            "gateway": gateway,
            "pool": f"{pool_start}-{pool_end}"
        }

    # =============================
    # USERS
    # =============================
    def create_user_profile(self, name, rate_limit="2M/2M"):
        if not self.exists("/ip hotspot user profile", f"name={name}"):
            self.exec(
                f'/ip hotspot user profile add name="{name}" rate-limit="{rate_limit}"'
            )

    def create_user(self, username, password, profile="default"):
        if not self.exists("/ip hotspot user", f"name=\"{username}\""):
            self.exec(
                f'/ip hotspot user add name="{username}" password="{password}" profile="{profile}"'
            )

    # =============================
    # BYPASS
    # =============================
    def add_bypass_ip(self, ip):
        if not self.exists("/ip hotspot ip-binding", f"address={ip}"):
            self.exec(f"/ip hotspot ip-binding add address={ip} type=bypassed")

    def list_bypass(self):
        return self.exec("/ip hotspot ip-binding print")