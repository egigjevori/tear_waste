from fastapi import APIRouter, Body
from starlette import status
from starlette.responses import JSONResponse

from app.services import authentication_service

authentication_router = APIRouter()


@authentication_router.post("/login")
async def login(
    username: str = Body(...),
    password: str = Body(...),
) -> JSONResponse:
    token = await authentication_service.authenticate(username, password)
    return JSONResponse({"access_token": token}, status_code=status.HTTP_200_OK)
