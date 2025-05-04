import time

import pytest
from unittest.mock import Mock

from src.models.service_instance import ServiceInstance
from src.models.health_status import HealthStatus
from src.router.round_robin_router import RoundRobinRouter


@pytest.mark.asyncio
async def test_unhealthy_instance_skipped():
    mock_instance_1 = Mock(spec=ServiceInstance)
    mock_instance_1.get_url.return_value = "http://localhost:9990"
    mock_instance_1.get_health_status.return_value = HealthStatus.HEALTHY

    mock_instance_2 = Mock(spec=ServiceInstance)
    mock_instance_2.get_url.return_value = "http://localhost:9991"
    mock_instance_2.get_health_status.return_value = HealthStatus.UNHEALTHY

    mock_instance_3 = Mock(spec=ServiceInstance)
    mock_instance_3.get_url.return_value = "http://localhost:9992"
    mock_instance_3.get_health_status.return_value = HealthStatus.HEALTHY

    instances = [mock_instance_1, mock_instance_2, mock_instance_3]

    mock_http_client = Mock()

    round_robin_router = RoundRobinRouter(instances=instances, http_client=mock_http_client)

    instance_url = await round_robin_router.get_next_service_instance()
    assert instance_url == "http://localhost:9990"

    instance_url = await round_robin_router.get_next_service_instance()
    assert instance_url == "http://localhost:9992"


@pytest.mark.asyncio
async def test_degraded_instance_skipped():
    mock_instance_1 = Mock(spec=ServiceInstance)
    mock_instance_1.get_url.return_value = "http://localhost:9990"
    mock_instance_1.get_health_status.return_value = HealthStatus.HEALTHY

    mock_instance_2 = Mock(spec=ServiceInstance)
    mock_instance_2.get_url.return_value = "http://localhost:9991"
    mock_instance_2.get_health_status.return_value = HealthStatus.DEGRADED

    mock_instance_3 = Mock(spec=ServiceInstance)
    mock_instance_3.get_url.return_value = "http://localhost:9992"
    mock_instance_3.get_health_status.return_value = HealthStatus.HEALTHY

    instances = [mock_instance_1, mock_instance_2, mock_instance_3]

    mock_http_client = Mock()

    round_robin_router = RoundRobinRouter(instances=instances, http_client=mock_http_client)

    instance_url = await round_robin_router.get_next_service_instance()
    assert instance_url == "http://localhost:9990"
    instance_url = await round_robin_router.get_next_service_instance()
    assert instance_url == "http://localhost:9992"
    instance_url = await round_robin_router.get_next_service_instance()
    assert instance_url == "http://localhost:9990"