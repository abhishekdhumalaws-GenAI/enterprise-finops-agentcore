from abc import ABC, abstractmethod


class BaseAgent(ABC):
    name: str

    @abstractmethod
    def handle(self, parsed_request):
        pass
