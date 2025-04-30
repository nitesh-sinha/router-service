from abc import ABC, abstractmethod

class Router(ABC):
    @abstractmethod
    async def route(self, endpoint:str, request_payload: dict) -> dict:
        pass
