import time

from src.models.health_status import HealthStatus


class ServiceInstance:
    def __init__(self, url: str):
        self.url = url
        self.health_status = HealthStatus.UNHEALTHY # assume every service instance is initially unhealthy
        self.last_healthcheck_time = time.time()
        self.state_transition_ctr = 0

    def update_health_status(self, new_status: HealthStatus):
        # TODO: use ctr=3 logic
        self.health_status = new_status

    def get_health_status(self):
        return self.health_status

    def get_url(self):
        return self.url

    def get_last_healthcheck_time(self):
        return self.last_healthcheck_time

    def update_last_healthcheck_time(self, check_time):
        self.last_healthcheck_time = check_time