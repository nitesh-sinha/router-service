import httpx
from src.utils.logger_config import setup_logger

logger = setup_logger(__name__)


class HttpClient:
    # response timeout can be instance variable
    async def post(self, url: str, payload: dict) -> dict:
        logger.info(f"Sending post request to {url}")
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(url, json=payload)
            logger.info(f"Obtained response for post {response.status_code}")
            response.raise_for_status()
            return response.json()

    async def get(self, url: str) -> dict:
        logger.info(f"Sending get request to {url}")
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(url)
            logger.info(f"Obtained response for get {response.status_code}")
            response.raise_for_status()
            return response.json()
