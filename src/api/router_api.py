from fastapi import APIRouter
from fastapi.responses import JSONResponse

from fastapi.exceptions import HTTPException
from src.router.router_factory import Router


def create_api_router(router: Router):
    api_router = APIRouter()

    @api_router.post("/echo")
    async def post(payload: dict):
        """
        POST endpoint of the router-service
        """
        try:
            response = await router.route("/echo", payload)
            return JSONResponse(content=response,status_code=200)
        except HTTPException as e:
            raise HTTPException(detail="Error processing the request", status_code=e.status_code)

    return api_router
