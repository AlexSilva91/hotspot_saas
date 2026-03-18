class BaseService:

    repository = None
    not_found_message = "Registro não encontrado"
    allowed_update_fields = None  # opcional

    # 🔹 CREATE
    @classmethod
    def create(cls, data):
        try:
            obj = cls.repository.create(data)

            return {
                "success": True,
                "data": obj
            }

        except Exception as e:
            return {
                "success": False,
                "errors": {
                    "general": str(e)
                }
            }

    # 🔹 LIST
    @classmethod
    def list(cls):
        try:
            data = cls.repository.get_all()

            return {
                "success": True,
                "data": data
            }

        except Exception as e:
            return {
                "success": False,
                "errors": {
                    "general": str(e)
                }
            }

    # 🔹 GET
    @classmethod
    def get(cls, obj_id):
        try:
            obj = cls.repository.get_by_id(obj_id)

            if not obj:
                return {
                    "success": False,
                    "errors": {
                        "not_found": cls.not_found_message
                    }
                }

            return {
                "success": True,
                "data": obj
            }

        except Exception as e:
            return {
                "success": False,
                "errors": {
                    "general": str(e)
                }
            }

    # 🔹 UPDATE
    @classmethod
    def update(cls, obj_id, data):
        try:
            obj = cls.repository.get_by_id(obj_id)

            if not obj:
                return {
                    "success": False,
                    "errors": {
                        "not_found": cls.not_found_message
                    }
                }

            # 🔒 Controle de campos
            if cls.allowed_update_fields:
                fields = cls.allowed_update_fields
            else:
                fields = data.keys()

            # Atualiza apenas os campos permitidos
            update_data = {}
            for key in fields:
                if key in data and data[key] is not None:
                    update_data[key] = data[key]

            # Usa o método update do repositório
            obj = cls.repository.update(obj, update_data)

            return {
                "success": True,
                "data": obj
            }

        except Exception as e:
            return {
                "success": False,
                "errors": {
                    "general": str(e)
                }
            }

    # 🔹 DELETE
    @classmethod
    def delete(cls, obj_id):
        try:
            obj = cls.repository.get_by_id(obj_id)

            if not obj:
                return {
                    "success": False,
                    "errors": {
                        "not_found": cls.not_found_message
                    }
                }

            cls.repository.delete(obj)

            return {
                "success": True
            }

        except Exception as e:
            return {
                "success": False,
                "errors": {
                    "general": str(e)
                }
            }