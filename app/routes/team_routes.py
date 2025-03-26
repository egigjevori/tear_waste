import logging

from fastapi import APIRouter, Body, Request
from starlette import status
from starlette.responses import JSONResponse

from app.services import authorization_service, team_service
from app.utils.permissions import Permission

logger = logging.getLogger(__name__)
team_router = APIRouter()


@team_router.post("/teams")
@authorization_service.require_permission(Permission.CREATE_TEAM)
async def create_team(_: Request, name: str = Body(...)) -> JSONResponse:
    logger.info(f"Received request to create team with name: {name}")
    await team_service.create_team(name)
    logger.info(f"Team '{name}' created successfully")
    return JSONResponse({"message": "Team created successfully"}, status_code=status.HTTP_201_CREATED)
