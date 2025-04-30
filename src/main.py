import asyncio
import time
import uvicorn
import logging

from fastapi import FastAPI
from src.models.service_instance import ServiceInstance
from src.router.router_factory import create_router
from src.health.health_checker import HealthChecker
from src.utils.http.http_client import HttpClient

app = FastAPI()
# TODO: Read from config file
config = {}
urls = ["http://localhost:23010", "http://localhost:23011", "http://localhost:23012", "http://localhost:23013"]
instances = [ServiceInstance(url) for url in urls]
router = create_router(config, instances)
health_checker = HealthChecker(instances, HttpClient(), config, time.time)

# TODO: Use APIRouter and move the apis to their own api module
@app.post("/echo")
async def echo(payload: dict):
    return await router.route("/echo", payload)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(health_checker.run())

if __name__ == "__main__":
    logger = logging.getLogger("router")
    logger.info("Starting the app")
    uvicorn.run(app, host="0.0.0.0", port=8000)