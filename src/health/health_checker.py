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
                 time_provider: time.time):
        self.svc_instances = instances
        self.http_client = http_client
        self.config = config
        self.time_provider = time_provider

    async def run(self):
        """
        Main loop to keep the healthchecker running every 
        health_check_interval seconds. It sends healthcheck
        requests to each downstream instance asynchronously.
        """
        while True:
            self.log_current_health_status()
            start = self.time_provider()
            tasks = [self.check_and_update_instance_health(instance) for instance in self.svc_instances]
            await asyncio.gather(*tasks)
            elapsed = self.time_provider() - start
            if elapsed < self.config["health_check_interval"]:
                await asyncio.sleep(self.config["health_check_interval"] - elapsed)

    async def check_and_update_instance_health(self, instance: ServiceInstance):
        """
        Given an instance, it checks its health by sending probe requests
        and categorizes its heath status based on the response time. It also
        updates the health status of the instance
        """
        logger.info(f"Starting health check for {instance.get_url()}")
        if self.skip_degraded_instance(instance):
            logger.info(f"Skipping healthcheck of DEGRADED instance {instance.get_url()}")
            return

        try:
            start_time = self.time_provider()
            try:
                async with asyncio.timeout(self.config['healthcheck_response_time_threshold']):
                    await self.http_client.get(instance.get_url() + "/health")
                    stop_time = self.time_provider()
                    response_time = stop_time - start_time
                    logger.info(f"Got healthcheck response for {instance.get_url()} in {response_time} seconds")
                    health_status = HealthStatus.HEALTHY
            except TimeoutError:
                logger.warning(f"Healthcheck timed out for {instance.get_url()}")
                health_status = HealthStatus.DEGRADED
        except Exception as e:
            logger.error(f"Error while getting health status for {instance.get_url()} : {str(e)}")
            health_status = HealthStatus.UNHEALTHY
        finally:
            # Use start_time instead of stop_time otherwise healthcheck
            # for DEGRADED instance is skipped for one extra healthcheck interval
            instance.update_health_status(health_status)
            instance.update_last_healthcheck_time(start_time)

    def skip_degraded_instance(self, instance: ServiceInstance) -> bool:
        """
        Determines whether healthcheck of a given instance can be skipped
        in the current healthcheck interval or not
        """
        now = self.time_provider()
        if (instance.health_status == HealthStatus.DEGRADED and
                (now - instance.get_last_healthcheck_time() < self.config['degraded_check_interval'])):
            return True
        return False

    def log_current_health_status(self):
        """
        Logs the health status of all configured downstream instances
        """
        logger.info("===================================================================")
        for instance in self.svc_instances:
            logger.info(
                f"[Health_Status_Summary] {instance.get_url()}   ->    {instance.get_health_status()}"
            )

        logger.info("===================================================================")
