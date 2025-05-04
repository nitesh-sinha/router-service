import asyncio
import time
import uvicorn
import logging
import json

from fastapi import FastAPI
from src.models.service_instance import ServiceInstance
from src.router.router_factory import create_router
from src.health.health_checker import HealthChecker
from src.utils.http.http_client import HttpClient
from src.api.router_api import create_api_router


def read_config_file() -> dict:
    with open('config.json', 'r', encoding='utf-8') as conf_file:
        config = json.load(conf_file)

    return config


def create_app(config: dict):
    """
    Creates the router API service and starts the healthchecker
    """
    app = FastAPI()
    urls = config['app_instances']
    instances = [ServiceInstance(url) for url in urls]
    router = create_router(config, instances)

    api_router = create_api_router(router)
    app.include_router(api_router)

    health_checker = HealthChecker(instances, HttpClient(), config, time.time)

    @app.on_event("startup")
    async def startup_event():
        asyncio.create_task(health_checker.run())

    return app


if __name__ == "__main__":
    logger = logging.getLogger("router-service")
    logger.info("Starting the app")
    config = read_config_file()
    app = create_app(config)
    uvicorn.run(app, host="0.0.0.0", port=config['router_port'])
