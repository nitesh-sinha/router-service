import asyncio

from src.router.base_router import Router
from src.utils.http.http_client import HttpClient
from src.models.service_instance import ServiceInstance
from src.models.health_status import HealthStatus
from src.utils.logger_config import setup_logger

logger = setup_logger(__name__)


class RoundRobinRouter(Router):
    def __init__(self, instances: list[ServiceInstance], http_client: HttpClient):
        self.svc_instances = instances
        self.http_client = http_client
        self.lock = asyncio.Lock()
        self.cur_index = 0 # Index into svc_instances list to select the next instance

    async def get_next_service_instance(self) -> str:
        logger.info("Starting to find next healthy instance....")
        async with self.lock:
            num_instances = len(self.svc_instances)
            for _ in range(num_instances):
                cur_instance = self.svc_instances[self.cur_index]
                self.cur_index = (self.cur_index + 1) % num_instances
                if cur_instance.get_health_status() == HealthStatus.HEALTHY:
                    return cur_instance.get_url()
                else:
                    logger.warning(f"Current instance {cur_instance.get_url()} is {cur_instance.get_health_status()}. "
                                   f"Skipping it!")

            logger.error("No healthy instances available")
            raise Exception("No healthy instances available")

    # endpoint should be like "/echo"
    async def route(self, endpoint: str, request_payload: dict) -> dict:
        target_url = await self.get_next_service_instance()
        return await self.http_client.post(target_url + endpoint, request_payload)
