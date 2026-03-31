# app/controller/router_controller/router_controller.py
from flask import request, flash, redirect, url_for, jsonify
from app.services.router_service import RouterService
from app.services.tenant_service import TenantService
from app.controller.base_controller import BaseController


class RouterController:
    
    @staticmethod
    def list():
        """Listar roteadores"""
        result = RouterService.list()
        routers = result.get("data", [])
        
        tenants_result = TenantService.list()
        tenants = tenants_result.get("data", [])
        
        return {
            "routers": routers,
            "tenants": tenants
        }
    
    @staticmethod
    def create():
        """Criar roteador"""
        data = {
            "name": request.form.get("name"),
            "ip_address": request.form.get("ip_address"),
            "api_port": int(request.form.get("api_port") or 8728),
            "username": request.form.get("username"),
            "password": request.form.get("password"),
            "location": request.form.get("location"),
            "tenant_id": request.form.get("tenant_id")
        }
        
        result = RouterService.create(data)
        
        return BaseController.handle_result(
            result=result,
            success_message="Roteador cadastrado com sucesso!",
            error_default="Erro ao cadastrar roteador",
            redirect_to="routers.list_routers"
        )
    
    @staticmethod
    def edit_page(router_id):
        """Página de edição de roteador"""
        result = RouterService.get(router_id)
        
        if not result.get("success"):
            flash(result.get("errors", {}).get("not_found", "Router não encontrado"), "error")
            return redirect(url_for("routers.list_routers"))
        
        router = result["data"]
        
        tenants_result = TenantService.list()
        tenants = tenants_result.get("data", [])
        
        return {
            "router": router,
            "tenants": tenants
        }
    
    @staticmethod
    def update(router_id):
        """Atualizar roteador"""
        data = {
            "name": request.form.get("name"),
            "ip_address": request.form.get("ip_address"),
            "api_port": int(request.form.get("api_port") or 8728),
            "username": request.form.get("username"),
            "password": request.form.get("password"),
            "location": request.form.get("location"),
            "tenant_id": request.form.get("tenant_id")
        }
        
        result = RouterService.update(router_id, data)
        
        return BaseController.handle_result(
            result=result,
            success_message="Roteador atualizado com sucesso!",
            error_default="Erro ao atualizar roteador",
            redirect_to="routers.list_routers"
        )
    
    @staticmethod
    def delete(router_id):
        """Deletar roteador"""
        result = RouterService.delete(router_id)
        
        return BaseController.handle_result(
            result=result,
            success_message="Roteador removido com sucesso!",
            error_default="Erro ao remover roteador",
            redirect_to="routers.list_routers"
        )
    
    @staticmethod
    def provision_hotspot(router_id):
        """
        Provisiona hotspot em um roteador.
        Recebe os dados da configuração via formulário.
        """
        # Extrai dados do formulário
        hotspot_config = {
            "bridge": request.form.get("bridge"),
            "lan": request.form.get("lan"),
            "lan_extras": request.form.getlist("lan_extras"),
            "wan": request.form.get("wan"),
            "pool": request.form.get("pool"),
            "ranges": request.form.get("ranges"),
            "ip": request.form.get("ip"),
            "network": request.form.get("network"),
            "gateway": request.form.get("gateway"),
            "user": request.form.get("hotspot_user"),
            "password": request.form.get("hotspot_password"),
            "dns_name": request.form.get("dns_name"),
            "lease_time": request.form.get("lease_time", "1h"),
            "hotspot": request.form.get("hotspot", "hotspot1"),
            "profile": request.form.get("profile", "hsprof1"),
            "dhcp": request.form.get("dhcp", "dhcp2")
        }
        
        # Remove campos vazios
        hotspot_config = {k: v for k, v in hotspot_config.items() if v}
        
        # Validações básicas
        required_fields = ["bridge", "lan", "pool", "ranges", "ip", "network", "gateway", "wan"]
        missing_fields = [field for field in required_fields if field not in hotspot_config]
        
        if missing_fields:
            flash(f"Campos obrigatórios faltando: {', '.join(missing_fields)}", "error")
            return redirect(url_for("routers.list_routers"))
        
        # Chama o serviço
        result = RouterService.provision_hotspot(router_id, hotspot_config)
        
        return BaseController.handle_result(
            result=result,
            success_message="Hotspot provisionado com sucesso!",
            error_default="Erro ao provisionar hotspot",
            redirect_to="routers.list_routers"
        )
    
    @staticmethod
    def remove_hotspot(router_id):
        """
        Remove hotspot de um roteador.
        Recebe os dados da configuração via formulário.
        """
        # Extrai dados do formulário
        hotspot_config = {
            "bridge": request.form.get("bridge"),
            "lan": request.form.get("lan"),
            "wan": request.form.get("wan"),
            "pool": request.form.get("pool"),
            "ip": request.form.get("ip"),
            "network": request.form.get("network"),
            "gateway": request.form.get("gateway"),
            "hotspot": request.form.get("hotspot", "hotspot1"),
            "profile": request.form.get("profile", "hsprof1"),
            "dhcp": request.form.get("dhcp", "dhcp2")
        }
        
        # Processa campos com múltiplos valores (separados por vírgula)
        lan_extras = request.form.get("lan_extras", "")
        if lan_extras:
            hotspot_config["lan_extras"] = [x.strip() for x in lan_extras.split(",") if x.strip()]
        else:
            hotspot_config["lan_extras"] = []
        
        users = request.form.get("users", "")
        if users:
            hotspot_config["users"] = [x.strip() for x in users.split(",") if x.strip()]
        else:
            hotspot_config["users"] = []
        
        user_profiles = request.form.get("user_profiles", "")
        if user_profiles:
            hotspot_config["user_profiles"] = [x.strip() for x in user_profiles.split(",") if x.strip()]
        else:
            hotspot_config["user_profiles"] = []
        
        bypass_macs = request.form.get("bypass_macs", "")
        if bypass_macs:
            hotspot_config["bypass_macs"] = [x.strip() for x in bypass_macs.split(",") if x.strip()]
        else:
            hotspot_config["bypass_macs"] = []
        
        # Remove campos vazios
        hotspot_config = {k: v for k, v in hotspot_config.items() if v}
        
        result = RouterService.remove_hotspot(router_id, hotspot_config)
        
        return BaseController.handle_result(
            result=result,
            success_message="Hotspot removido com sucesso!",
            error_default="Erro ao remover hotspot",
            redirect_to="routers.list_routers"
        )

        
        