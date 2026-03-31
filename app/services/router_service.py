# app/services/router_service.py
from app.services.base_service import BaseService
from app.repositories.router_repository import RouterRepository
from app.decorators.plan_limit import enforce_plan_limits
import asyncio
from app.services.mikrotik_ssh_service import MikroTikSSHService


class RouterService(BaseService):
    repository = RouterRepository
    not_found_message = "Router não encontrado"

    @classmethod
    @enforce_plan_limits(resource="router")
    def create(cls, data):
        return super().create(data)

    @classmethod
    def update(cls, obj_id, data):
        return super().update(obj_id, data)

    @classmethod
    def provision_hotspot(cls, router_id, hotspot_config):
        """
        Provisiona hotspot em um roteador específico.
        
        Args:
            router_id: ID do roteador
            hotspot_config: Dicionário com configurações do hotspot
        
        Returns:
            dict: Resultado da operação com success, message e dados
        """
        try:
            # Busca os dados do roteador no repositório
            router = cls.repository.get_by_id(router_id)
            
            if not router:
                return {
                    "success": False,
                    "errors": {"not_found": cls.not_found_message}
                }
            
            # Extrai dados de conexão do roteador
            host = router.ip_address
            username = router.username
            password = router.password
            port = getattr(router, 'ssh_port', 22)
            
            # Cria instância do serviço SSH
            ssh_service = MikroTikSSHService(
                host=host,
                username=username,
                password=password,
                port=port,
                timeout=10
            )
            
            # Executa o provisionamento de forma assíncrona
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                # Conecta e provisiona
                loop.run_until_complete(ssh_service.connect())
                loop.run_until_complete(ssh_service.setup_hotspot(hotspot_config))
                
                # Atualiza o status do router no banco de dados
                router.hotspot_provisioned = True
                router.hotspot_config = hotspot_config
                cls.repository.update(router, {})
                
                return {
                    "success": True,
                    "message": "Hotspot provisionado com sucesso!",
                    "data": {
                        "router_id": str(router.id),
                        "router_name": router.name,
                        "hotspot_config": hotspot_config
                    }
                }
                
            except Exception as e:
                return {
                    "success": False,
                    "errors": {"provision": f"Erro ao provisionar hotspot: {str(e)}"}
                }
            finally:
                # Garante que a conexão seja fechada
                try:
                    loop.run_until_complete(ssh_service.close())
                except:
                    pass
                loop.close()
                
        except Exception as e:
            return {
                "success": False,
                "errors": {"service": f"Erro no serviço: {str(e)}"}
            }
    
    @classmethod
    def remove_hotspot(cls, router_id, hotspot_config):
        """
        Remove hotspot de um roteador específico.
        
        Args:
            router_id: ID do roteador
            hotspot_config: Configuração do hotspot a ser removido
        """
        try:
            # Busca os dados do roteador
            router = cls.repository.get_by_id(router_id)
            
            if not router:
                return {
                    "success": False,
                    "errors": {"not_found": cls.not_found_message}
                }
            
            # Cria instância do serviço SSH
            ssh_service = MikroTikSSHService(
                host=router.ip_address,
                username=router.username,
                password=router.password,
                port=getattr(router, 'ssh_port', 22)
            )
            
            # Executa a remoção
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                loop.run_until_complete(ssh_service.connect())
                loop.run_until_complete(ssh_service.teardown_hotspot(hotspot_config))
                
                # Atualiza o status do router no banco de dados
                router.hotspot_provisioned = False
                router.hotspot_config = None
                cls.repository.update(router, {})
                
                return {
                    "success": True,
                    "message": "Hotspot removido com sucesso!",
                    "data": {"router_id": str(router.id)}
                }
                
            except Exception as e:
                return {
                    "success": False,
                    "errors": {"remove": f"Erro ao remover hotspot: {str(e)}"}
                }
            finally:
                try:
                    loop.run_until_complete(ssh_service.close())
                except:
                    pass
                loop.close()
                
        except Exception as e:
            return {
                "success": False,
                "errors": {"service": f"Erro no serviço: {str(e)}"}
            }