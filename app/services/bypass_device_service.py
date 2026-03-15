from app.repositories.bypass_device_repository import BypassDeviceRepository


class BypassDeviceService:


    @staticmethod
    def create_device(data):

        return BypassDeviceRepository.create(data)


    @staticmethod
    def list_devices():

        return BypassDeviceRepository.get_all()


    @staticmethod
    def get_device(device_id):

        device = BypassDeviceRepository.get_by_id(device_id)

        if not device:
            raise Exception("Dispositivo não encontrado")

        return device


    @staticmethod
    def update_device(device_id, data):

        device = BypassDeviceRepository.get_by_id(device_id)

        if not device:
            raise Exception("Dispositivo não encontrado")

        for key, value in data.items():
            setattr(device, key, value)

        return BypassDeviceRepository.save(device)


    @staticmethod
    def delete_device(device_id):

        device = BypassDeviceRepository.get_by_id(device_id)

        if not device:
            raise Exception("Dispositivo não encontrado")

        BypassDeviceRepository.delete(device)