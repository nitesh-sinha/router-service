from src.models.service_instance import ServiceInstance
from src.utils.http.http_client import HttpClient
from src.router.base_router import Router
from src.router.round_robin_router import RoundRobinRouter


def create_router(config: dict, svc_instances: list[ServiceInstance]) -> Router:
    """
    Uses factory design pattern to create an appropriate router service
    based on the routing algorithm in config.json
    """
    routing_algo = config["routing_algorithm"]
    http_client = HttpClient()

    if routing_algo == "round_robin":
        return RoundRobinRouter(svc_instances, http_client)
    else:
        raise ValueError(f"Unknown routing algorithm {routing_algo}")
