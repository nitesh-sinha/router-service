import time
import asyncio

import pytest
from unittest.mock import Mock, AsyncMock
from fastapi import HTTPException

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


@pytest.mark.asyncio
async def test_no_healthy_instances_returns_none():
    mock_instance_1 = Mock(spec=ServiceInstance)
    mock_instance_1.get_url.return_value = "http://localhost:9990"
    mock_instance_1.get_health_status.return_value = HealthStatus.UNHEALTHY

    mock_instance_2 = Mock(spec=ServiceInstance)
    mock_instance_2.get_url.return_value = "http://localhost:9991"
    mock_instance_2.get_health_status.return_value = HealthStatus.DEGRADED

    instances = [mock_instance_1, mock_instance_2]
    mock_http_client = Mock()
    
    round_robin_router = RoundRobinRouter(instances=instances, http_client=mock_http_client)
    
    instance_url = await round_robin_router.get_next_service_instance()
    assert instance_url is None


@pytest.mark.asyncio
async def test_empty_instances_list_returns_none():
    instances = []
    mock_http_client = Mock()
    
    round_robin_router = RoundRobinRouter(instances=instances, http_client=mock_http_client)
    
    instance_url = await round_robin_router.get_next_service_instance()
    assert instance_url is None


@pytest.mark.asyncio
async def test_round_robin_cycling_behavior():
    mock_instance_1 = Mock(spec=ServiceInstance)
    mock_instance_1.get_url.return_value = "http://localhost:9990"
    mock_instance_1.get_health_status.return_value = HealthStatus.HEALTHY

    mock_instance_2 = Mock(spec=ServiceInstance)
    mock_instance_2.get_url.return_value = "http://localhost:9991"
    mock_instance_2.get_health_status.return_value = HealthStatus.HEALTHY

    instances = [mock_instance_1, mock_instance_2]
    mock_http_client = Mock()
    
    round_robin_router = RoundRobinRouter(instances=instances, http_client=mock_http_client)
    
    # Test multiple cycles
    assert await round_robin_router.get_next_service_instance() == "http://localhost:9990"
    assert await round_robin_router.get_next_service_instance() == "http://localhost:9991"
    assert await round_robin_router.get_next_service_instance() == "http://localhost:9990"
    assert await round_robin_router.get_next_service_instance() == "http://localhost:9991"


@pytest.mark.asyncio
async def test_route_successful_request():
    mock_instance = Mock(spec=ServiceInstance)
    mock_instance.get_url.return_value = "http://localhost:9990"
    mock_instance.get_health_status.return_value = HealthStatus.HEALTHY

    instances = [mock_instance]
    mock_http_client = Mock()
    expected_response = {"status": "success", "data": "test"}
    mock_http_client.post = AsyncMock(return_value=expected_response)
    
    round_robin_router = RoundRobinRouter(instances=instances, http_client=mock_http_client)
    
    response = await round_robin_router.route("/echo", {"test": "data"})
    
    assert response == expected_response
    mock_http_client.post.assert_called_once_with("http://localhost:9990/echo", {"test": "data"})


@pytest.mark.asyncio
async def test_route_no_healthy_instances_raises_exception():
    mock_instance = Mock(spec=ServiceInstance)
    mock_instance.get_url.return_value = "http://localhost:9990"
    mock_instance.get_health_status.return_value = HealthStatus.UNHEALTHY

    instances = [mock_instance]
    mock_http_client = Mock()
    
    round_robin_router = RoundRobinRouter(instances=instances, http_client=mock_http_client)
    
    with pytest.raises(HTTPException) as exc_info:
        await round_robin_router.route("/echo", {"test": "data"})
    
    assert exc_info.value.status_code == 500
    assert "No healthy downstream instance available" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_route_http_client_error_raises_exception():
    mock_instance = Mock(spec=ServiceInstance)
    mock_instance.get_url.return_value = "http://localhost:9990"
    mock_instance.get_health_status.return_value = HealthStatus.HEALTHY

    instances = [mock_instance]
    mock_http_client = Mock()
    mock_http_client.post = AsyncMock(side_effect=Exception("Connection failed"))
    
    round_robin_router = RoundRobinRouter(instances=instances, http_client=mock_http_client)
    
    with pytest.raises(HTTPException) as exc_info:
        await round_robin_router.route("/echo", {"test": "data"})
    
    assert exc_info.value.status_code == 500
    assert "Error received from downstream instance" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_route_propagates_http_exceptions():
    mock_instance = Mock(spec=ServiceInstance)
    mock_instance.get_url.return_value = "http://localhost:9990"
    mock_instance.get_health_status.return_value = HealthStatus.HEALTHY

    instances = [mock_instance]
    mock_http_client = Mock()
    original_exception = HTTPException(status_code=404, detail="Not found")
    mock_http_client.post = AsyncMock(side_effect=original_exception)
    
    round_robin_router = RoundRobinRouter(instances=instances, http_client=mock_http_client)
    
    with pytest.raises(HTTPException) as exc_info:
        await round_robin_router.route("/echo", {"test": "data"})
    
    assert exc_info.value == original_exception


@pytest.mark.asyncio
async def test_concurrent_access_thread_safety():
    mock_instance_1 = Mock(spec=ServiceInstance)
    mock_instance_1.get_url.return_value = "http://localhost:9990"
    mock_instance_1.get_health_status.return_value = HealthStatus.HEALTHY

    mock_instance_2 = Mock(spec=ServiceInstance)
    mock_instance_2.get_url.return_value = "http://localhost:9991"
    mock_instance_2.get_health_status.return_value = HealthStatus.HEALTHY

    instances = [mock_instance_1, mock_instance_2]
    mock_http_client = Mock()
    
    round_robin_router = RoundRobinRouter(instances=instances, http_client=mock_http_client)
    
    # Simulate concurrent access
    tasks = [round_robin_router.get_next_service_instance() for _ in range(10)]
    results = await asyncio.gather(*tasks)
    
    # Verify we get alternating instances (round-robin behavior)
    expected = ["http://localhost:9990", "http://localhost:9991"] * 5
    assert results == expected