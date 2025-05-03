import logging
import time

from src.models.health_status import HealthStatus
from src.utils.logger_config import setup_logger

logger = setup_logger(__name__)

class ServiceInstance:
    def __init__(self, url: str):
        self.url = url
        self.health_status = HealthStatus.UNHEALTHY # assume every service instance is initially unhealthy
        self.last_healthcheck_time = time.time()
        self.state_transition_ctr = 0

    def update_health_status(self, new_status: HealthStatus):
        if new_status == self.health_status:
            return

        self.state_transition_ctr += 1
        logger.info(f"New health status of {new_status} received for {self.url}")
        if self.state_transition_ctr < 3:
            logger.info(f"Will monitor for {3 - self.state_transition_ctr} more intervals before transitioning")
            return

        self.health_status = new_status
        self.state_transition_ctr = 0
        logger.info(f"Transitioned {self.url} to {new_status}")


    def get_health_status(self):
        return self.health_status

    def get_url(self):
        return self.url

    def get_last_healthcheck_time(self):
        return self.last_healthcheck_time

    def update_last_healthcheck_time(self, check_time):
        self.last_healthcheck_time = check_time