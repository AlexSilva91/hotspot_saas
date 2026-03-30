import asyncio
from app.services.base_service import BaseService
from app.repositories.bypass_device_repository import BypassDeviceRepository
from app.services.mikrotik_ssh_service import MikroTikSSHService


class BypassDeviceService(BaseService):
    repository = BypassDeviceRepository
    not_found_message = "Dispositivo não encontrado"

    # =========================================================================
    # HELPERS SSH
    # =========================================================================

    @classmethod
    def _get_ssh(cls, router):
        return MikroTikSSHService(
            host=router.ip_address,
            username=router.username,
            password=router.password,
            port=getattr(router, "port", 22),
        )

    # =========================================================================
    # CREATE — SSH primeiro, DB depois
    # =========================================================================

    @classmethod
    def create(cls, data):
        try:
            device = cls.repository.get_by_mac_and_router(
                data.get("mac_address"), data.get("router_id")
            )
            if device:
                return {"success": False, "errors": {"general": "MAC já cadastrado neste roteador."}}

            router = cls.repository.get_router(data.get("router_id"))
            if not router:
                return {"success": False, "errors": {"general": "Roteador não encontrado."}}

            async def _run():
                ssh = cls._get_ssh(router)
                await ssh.connect()
                try:
                    await ssh.add_bypass_mac(
                        mac=data["mac_address"],
                        server=router.hotspot_name,
                        comment=data.get("comment", ""),
                    )
                finally:
                    await ssh.close()

            asyncio.run(_run())

            obj = cls.repository.create(data)
            return {"success": True, "data": obj}

        except Exception as e:
            return {"success": False, "errors": {"general": str(e)}}

    # =========================================================================
    # UPDATE — SSH primeiro, DB depois
    # =========================================================================

    @classmethod
    def update(cls, obj_id, data):
        try:
            device = cls.repository.get_by_id(obj_id)
            if not device:
                return {"success": False, "errors": {"not_found": cls.not_found_message}}

            router = cls.repository.get_router(device.router_id)
            if not router:
                return {"success": False, "errors": {"general": "Roteador vinculado não encontrado."}}

            old_mac      = device.mac_address
            new_mac      = data.get("mac_address", old_mac)
            new_comment  = data.get("comment", device.comment)
            new_type     = data.get("binding_type", device.binding_type)
            new_active   = data.get("active", device.active)

            async def _run():
                ssh = cls._get_ssh(router)
                await ssh.connect()
                try:
                    # Remove o binding antigo e recria com todos os novos dados
                    await ssh.safe_remove(
                        f"/ip hotspot ip-binding remove [find mac-address={old_mac}]"
                    )
                    await ssh.add_bypass_mac(
                        mac=new_mac,
                        server=getattr(router, "hotspot_name", None) or "all",
                        comment=new_comment,
                    )
                    # Aplica o type correto (add_bypass_mac cria sempre como bypassed)
                    if new_type != "bypassed":
                        await ssh.set_binding_type(new_mac, new_type)
                    # Aplica disabled se inativo
                    if not new_active:
                        await ssh.disable_bypass_mac(new_mac)

                finally:
                    await ssh.close()

            asyncio.run(_run())

            obj = cls.repository.update(device, {
                "mac_address":  new_mac,
                "comment":      new_comment,
                "binding_type": new_type,
                "active":       new_active,
            })
            return {"success": True, "data": obj}

        except Exception as e:
            return {"success": False, "errors": {"general": str(e)}}

    # =========================================================================
    # DELETE — desativa no MikroTik (disabled=yes), não remove do DB
    # =========================================================================
    @classmethod
    def delete(cls, obj_id):
        try:
            device = cls.repository.get_by_id(obj_id)
            if not device:
                return {"success": False, "errors": {"not_found": cls.not_found_message}}

            router = cls.repository.get_router(device.router_id)
            if not router:
                return {"success": False, "errors": {"general": "Roteador vinculado não encontrado."}}

            async def _run():
                ssh = cls._get_ssh(router)
                await ssh.connect()
                try:
                    await ssh.disable_bypass_mac(device.mac_address)
                finally:
                    await ssh.close()

            asyncio.run(_run())

            obj = cls.repository.update(device, {
                "active": False,
                "binding_type": "blocked"
            })
            return {"success": True, "data": obj}

        except Exception as e:
            return {"success": False, "errors": {"general": str(e)}}

    @classmethod
    def enable(cls, obj_id):
        try:
            device = cls.repository.get_by_id(obj_id)
            if not device:
                return {"success": False, "errors": {"not_found": cls.not_found_message}}

            router = cls.repository.get_router(device.router_id)
            if not router:
                return {"success": False, "errors": {"general": "Roteador vinculado não encontrado."}}

            async def _run():
                ssh = cls._get_ssh(router)
                await ssh.connect()
                try:
                    await ssh.enable_bypass_mac(device.mac_address)
                finally:
                    await ssh.close()

            asyncio.run(_run())

            obj = cls.repository.update(device, {
                "active": True,
                "binding_type": "regular"
            })
            return {"success": True, "data": obj}

        except Exception as e:
            return {"success": False, "errors": {"general": str(e)}}

    # =========================================================================
    # CHANGE TYPE — muda blocked | bypassed | regular
    # =========================================================================

    @classmethod
    def change_type(cls, obj_id, new_type):
        try:
            device = cls.repository.get_by_id(obj_id)
            if not device:
                return {"success": False, "errors": {"not_found": cls.not_found_message}}

            router = cls.repository.get_router(device.router_id)
            if not router:
                return {"success": False, "errors": {"general": "Roteador vinculado não encontrado."}}

            async def _run():
                ssh = cls._get_ssh(router)
                await ssh.connect()
                try:
                    await ssh.set_binding_type(device.mac_address, new_type)
                finally:
                    await ssh.close()

            asyncio.run(_run())

            obj = cls.repository.update(device, {"binding_type": new_type})
            return {"success": True, "data": obj}

        except Exception as e:
            return {"success": False, "errors": {"general": str(e)}}