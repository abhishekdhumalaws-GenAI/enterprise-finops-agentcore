from abc import ABC, abstractmethod


class BaseTool(ABC):
    name: str

    @abstractmethod
    def execute(self, *args, **kwargs):
        pass

    def success_response(self, data):
        return {
            "success": True,
            "data": data,
            "error": None
        }

    def error_response(self, error_type, message):
        return {
            "success": False,
            "data": None,
            "error": {
                "type": error_type,
                "message": message
            }
        }
