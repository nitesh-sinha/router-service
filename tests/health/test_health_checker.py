import asyncio
import time

import pytest
from unittest.mock import AsyncMock, Mock, MagicMock

from src.models.service_instance import ServiceInstance
from src.models.health_status import HealthStatus
from src.health.health_checker import HealthChecker


@pytest.mark.asyncio
async def test_healthcheck_times_out_sets_instance_degraded():
    cur_time = time.time()
    mock_svc_instance = Mock(spec=ServiceInstance)
    mock_svc_instance.get_url.return_value = "http://localhost:9999"
    mock_svc_instance.health_status = HealthStatus.HEALTHY
    mock_svc_instance.get_last_healthcheck_time.return_value = cur_time
    mock_svc_instance.update_health_status = MagicMock()

    mock_http_client = Mock()
    async def delayed_get(url):
        await asyncio.sleep(2.2)
    mock_http_client.get = AsyncMock(side_effect=delayed_get)

    mock_time_provider = Mock()
    start_time = cur_time
    stop_time = cur_time + 2
    mock_time_provider.side_effect = [start_time, stop_time]

    mock_config = {
        'healthcheck_response_time_threshold': 2
    }

    health_checker = HealthChecker(instances=[mock_svc_instance],
                                   http_client=mock_http_client,
                                   config=mock_config,
                                   time_provider=mock_time_provider)

    await health_checker.check_instance_health(mock_svc_instance)

    mock_svc_instance.update_health_status.assert_called_once_with(HealthStatus.DEGRADED)


@pytest.mark.asyncio
async def test_healthcheck_errors_out_sets_instance_unhealthy():
    cur_time = time.time()
    mock_svc_instance = Mock(spec=ServiceInstance)
    mock_svc_instance.get_url.return_value = "http://localhost:9999"
    mock_svc_instance.health_status = HealthStatus.HEALTHY
    mock_svc_instance.get_last_healthcheck_time.return_value = cur_time
    mock_svc_instance.update_health_status = MagicMock()

    mock_http_client = Mock()
    async def errored_get(url):
        raise BrokenPipeError()
    mock_http_client.get = AsyncMock(side_effect=errored_get)

    mock_time_provider = Mock()
    start_time = cur_time
    stop_time = cur_time + 2
    mock_time_provider.side_effect = [start_time, stop_time]

    mock_config = {
        'healthcheck_response_time_threshold': 2
    }

    health_checker = HealthChecker(instances=[mock_svc_instance],
                                   http_client=mock_http_client,
                                   config=mock_config,
                                   time_provider=mock_time_provider)

    await health_checker.check_instance_health(mock_svc_instance)

    mock_svc_instance.update_health_status.assert_called_once_with(HealthStatus.UNHEALTHY)


@pytest.mark.asyncio
async def test_healthcheck_passes_sets_instance_healthy():
    cur_time = time.time()
    mock_svc_instance = Mock(spec=ServiceInstance)
    mock_svc_instance.get_url.return_value = "http://localhost:9999"
    mock_svc_instance.health_status = HealthStatus.UNHEALTHY
    mock_svc_instance.get_last_healthcheck_time.return_value = cur_time
    mock_svc_instance.update_health_status = MagicMock()

    mock_http_client = Mock()
    async def successful_get(url):
        await asyncio.sleep(0.5)
    mock_http_client.get = AsyncMock(side_effect=successful_get)

    mock_time_provider = Mock()
    start_time = cur_time
    mock_time_provider.side_effect = [start_time, start_time + 2, start_time + 3]

    mock_config = {
        'healthcheck_response_time_threshold': 5
    }

    health_checker = HealthChecker(instances=[mock_svc_instance],
                                   http_client=mock_http_client,
                                   config=mock_config,
                                   time_provider=mock_time_provider)

    await health_checker.check_instance_health(mock_svc_instance)

    mock_svc_instance.update_health_status.assert_called_once_with(HealthStatus.HEALTHY)



@pytest.mark.asyncio
async def test_healthcheck_skips_degraded_instance():
    cur_time = time.time()
    mock_svc_instance = Mock(spec=ServiceInstance)
    mock_svc_instance.get_url.return_value = "http://localhost:9999"
    mock_svc_instance.health_status = HealthStatus.DEGRADED
    mock_svc_instance.get_last_healthcheck_time.return_value = cur_time - 10
    mock_svc_instance.update_health_status = MagicMock()

    mock_http_client = Mock()
    async def successful_get(url):
        await asyncio.sleep(0.5)
    mock_http_client.get = AsyncMock(side_effect=successful_get)

    mock_time_provider = Mock()
    start_time = cur_time
    mock_time_provider.side_effect = [start_time, start_time + 2, start_time + 3]

    mock_config = {
        'healthcheck_response_time_threshold': 5,
        'degraded_check_interval': 30
    }

    health_checker = HealthChecker(instances=[mock_svc_instance],
                                   http_client=mock_http_client,
                                   config=mock_config,
                                   time_provider=mock_time_provider)

    await health_checker.check_instance_health(mock_svc_instance)

    mock_svc_instance.update_health_status.assert_not_called()


@pytest.mark.asyncio
async def test_healthcheck_does_not_skip_degraded_instance():
    cur_time = time.time()
    mock_svc_instance = Mock(spec=ServiceInstance)
    mock_svc_instance.get_url.return_value = "http://localhost:9999"
    mock_svc_instance.health_status = HealthStatus.DEGRADED
    mock_svc_instance.get_last_healthcheck_time.return_value = cur_time - 40
    mock_svc_instance.update_health_status = MagicMock()

    mock_http_client = Mock()
    async def successful_get(url):
        await asyncio.sleep(0.5)
    mock_http_client.get = AsyncMock(side_effect=successful_get)

    mock_time_provider = Mock()
    start_time = cur_time
    mock_time_provider.side_effect = [start_time, start_time + 2, start_time + 3]

    mock_config = {
        'healthcheck_response_time_threshold': 5,
        'degraded_check_interval': 30
    }

    health_checker = HealthChecker(instances=[mock_svc_instance],
                                   http_client=mock_http_client,
                                   config=mock_config,
                                   time_provider=mock_time_provider)

    await health_checker.check_instance_health(mock_svc_instance)

    mock_svc_instance.update_health_status.assert_called_once_with(HealthStatus.HEALTHY)