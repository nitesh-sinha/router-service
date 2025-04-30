import asyncio
import time
from src.utils.logger_config import setup_logger

from src.utils.http.http_client import HttpClient
from src.models.service_instance import ServiceInstance
from src.models.health_status import HealthStatus

logger = setup_logger(__name__)


class HealthChecker:
    def __init__(self, instances: list[ServiceInstance],
                 http_client: HttpClient,
                 config: dict,
                 time: time.time):
        self.svc_instances = instances
        self.http_client = http_client
        self.config = config
        self.time_provider = time

    async def run(self):
        while True:
            start = self.time_provider()
            tasks = [self.check_instance_health(instance) for instance in self.svc_instances]
            await asyncio.gather(*tasks)
            elapsed = self.time_provider() - start
            #await asyncio.sleep(self.config["health_check_interval"])
            if elapsed < 10:
                await asyncio.sleep(10 - elapsed)

    async def check_instance_health(self, instance: ServiceInstance):
        logger.info(f"Starting health check for {instance.get_url()}")
        if self.skip_degraded_instance(instance):
            return

        try:
            start_time = self.time_provider()
            try:
                async with asyncio.timeout(5):
                    await self.http_client.get(instance.get_url() + "/health")
                    logger.info(f"Got healthcheck response for {instance.get_url()}")
                    stop_time = self.time_provider()
                    response_time = stop_time - start_time
                    logger.info(f"Healthcheck response time for {instance.get_url()} is {response_time}")
                    health_status = self.determine_health_status(response_time)
            except TimeoutError:
                logger.warning(f"Healthcheck timed out for {instance.get_url()}")
                health_status = HealthStatus.DEGRADED
            logger.info(f"Health status for {instance.get_url()} is {health_status}")
            instance.update_health_status(health_status)
        except Exception as e:
            logger.error(f"Health status for {instance.get_url()} is UNHEALTHY: {str(e)}")
            instance.update_health_status(HealthStatus.UNHEALTHY)
        finally:
            # Use start_time instead of stop_time otherwise healthcheck
            # for DEGRADED instance is skipped for one more 10sec interval
            instance.update_last_healthcheck_time(start_time)

    def skip_degraded_instance(self, instance: ServiceInstance) -> bool:
        now = self.time_provider()
        # Use degraded_check_interval instead of 30
        if (instance.health_status == HealthStatus.DEGRADED and
                (now - instance.get_last_healthcheck_time() < 30)):
            logger.info(f"Skipping healthcheck of DEGRADED instance {instance.get_url()}")
            return True

        return False

    def determine_health_status(self, response_time: float) -> HealthStatus:
        if response_time < 5:
            return HealthStatus.HEALTHY
