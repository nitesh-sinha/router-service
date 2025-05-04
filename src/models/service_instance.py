import logging
import time

from src.models.health_status import HealthStatus
from src.utils.logger_config import setup_logger

logger = setup_logger(__name__)


class ServiceInstance:
    def __init__(self, url: str):
        self.url = url
        # assume every service instance starts out as unhealthy
        self.health_status = HealthStatus.UNHEALTHY 
        self.last_healthcheck_time = time.time()
        self.state_transition_ctr = 0
        self.min_state_transition_requests = 3

    def update_health_status(self, new_status: HealthStatus):
        """
        Updates the health status only after receiving 
        min_state_transition_requests consecutive requests
        with same health status 
        """
        if new_status == self.health_status:
            return

        self.state_transition_ctr += 1
        logger.info(f"New health status of {new_status} received for {self.url}")
        if self.state_transition_ctr < self.min_state_transition_requests:
            logger.info(f"Will monitor for {self.min_state_transition_requests - self.state_transition_ctr} "
                        f"more intervals before transitioning")
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
        