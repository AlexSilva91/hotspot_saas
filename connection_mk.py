import socket
from app.services.mikrotik_ssh_service import MikroTikSSHService


class Router:
    def __init__(self, ip_address, username, password, port=22):
        self.ip_address = ip_address
        self.username = username
        self.password = password
        self.port = port


# =============================
# TESTE DE PORTA (SSH)
# =============================
def test_port(host, port=22):
    try:
        s = socket.create_connection((host, port), timeout=3)
        s.close()
        return True
    except Exception as e:
        return False


# =============================
# TESTE COMPLETO DO SERVICE
# =============================
def test_connection(router):
    print("=" * 50)
    print(f"🔎 Testando SSH em {router.ip_address}")
    print("=" * 50)

    # 1. Porta SSH
    if not test_port(router.ip_address, router.port):
        print("❌ Porta 22 fechada (SSH não acessível)")
        return

    print("✅ Porta 22 OK")

    mk = MikroTikSSHService(
        router.ip_address,
        router.username,
        router.password,
        router.port
    )

    try:
        # 2. Conectar
        print("\n🔐 Conectando...")
        mk.connect()
        print("✅ Conectado via SSH")

        # 3. Identity
        print("\n📌 Identidade do roteador:")
        identity = mk.exec("/system identity print")
        print(identity)

        # 4. Interfaces
        print("\n📡 Interfaces disponíveis:")
        interfaces = mk.exec("/interface print")
        print(interfaces)

        # 5. Criar Hotspot
        print("\n🚀 Criando HOTSPOT...")

        result = mk.create_hotspot(
            interface="ether3",
            network_cidr="192.168.100.0/24"
        )

        print("✅ Hotspot criado com sucesso:")
        print(result)

        # 6. Criar profile
        print("\n👤 Criando profile...")
        mk.create_user_profile("teste_plano", "2M/2M")
        print("✅ Profile criado")

        # 7. Criar usuário
        print("\n👥 Criando usuário...")
        mk.create_user("teste_user", "123", "teste_plano")
        print("✅ Usuário criado")

        # 8. Bypass
        print("\n🚫 Criando bypass...")
        mk.add_bypass_ip("192.168.100.10")
        print("✅ Bypass criado")

        print("\n📡 Lista de bypass:")
        print(mk.list_bypass())

        # 9. Validação final
        print("\n🔍 VALIDAÇÃO FINAL:")

        print("\n➡ Hotspot:")
        print(mk.exec("/ip hotspot print"))

        print("\n➡ DHCP:")
        print(mk.exec("/ip dhcp-server print"))

        print("\n➡ IP Address:")
        print(mk.exec("/ip address print"))

        print("\n➡ NAT:")
        print(mk.exec("/ip firewall nat print"))

        print("\n🎯 TESTE COMPLETO FINALIZADO COM SUCESSO")

    except Exception as e:
        print("\n❌ Falha no SERVICE:")
        print(f"Tipo: {type(e).__name__}")
        print(f"Erro: {str(e)}")

    finally:
        mk.close()
        print("\n🔌 Conexão encerrada")


# =============================
# EXECUÇÃO
# =============================
if __name__ == "__main__":
    router = Router(
        ip_address="172.16.0.3",
        username="admin",
        password="admin"
    )

    test_connection(router)