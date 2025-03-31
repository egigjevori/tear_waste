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
async def create_team(request: Request, name: str = Body(..., embed=True)) -> JSONResponse:
    logger.info(f"Received request to create team with name: {name}")
    team = await team_service.create_team(name)
    logger.info(f"Team '{name}' created successfully")
    return JSONResponse(team.to_dict(), status_code=status.HTTP_201_CREATED)


@team_router.get("/teams")
@authorization_service.require_permission(Permission.GET_ALL_TEAMS)
async def get_all_teams() -> JSONResponse:
    logger.info("Received request to get all teams")
    teams = await team_service.get_all_teams()
    return JSONResponse([team.to_dict() for team in teams], status_code=status.HTTP_200_OK)
