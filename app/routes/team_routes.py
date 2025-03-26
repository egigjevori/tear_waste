from fastapi import APIRouter, Body, Request
from starlette import status
from starlette.responses import JSONResponse

from app.services import authorization_service, team_service
from app.utils.permissions import Permission

team_router = APIRouter()


@team_router.post("/teams")
@authorization_service.require_permission(Permission.CREATE_TEAM)
async def create_team(request: Request, name: str = Body(...)) -> JSONResponse:
    await team_service.create_team(name)
    return JSONResponse({"message": "Team created successfully"}, status_code=status.HTTP_201_CREATED)
