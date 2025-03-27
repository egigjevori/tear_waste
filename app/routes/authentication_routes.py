import logging

from fastapi import APIRouter, Body, Request
from starlette import status
from starlette.responses import JSONResponse

from app.services import authentication_service

logger = logging.getLogger(__name__)

authentication_router = APIRouter()


@authentication_router.post("/login")
async def login(
    request: Request,
    username: str = Body(...),
    password: str = Body(...),
) -> JSONResponse:
    logger.info(f"Login attempt for user: {username}")
    token = await authentication_service.authenticate(username, password)
    logger.info(f"User {username} authenticated successfully")
    return JSONResponse({"access_token": token}, status_code=status.HTTP_200_OK)
