from fastapi import Body, Request
from starlette import status
from starlette.responses import JSONResponse

from app.services import team_service, authentication_service, authorization_service
from fastapi import APIRouter

from app.utils.permissions import Permission

team_router = APIRouter()


@team_router.post("/teams")
@authorization_service.require_permission(Permission.CREATE_TEAM)
async def create_team(request: Request, name: str = Body(...)) -> JSONResponse:
    await team_service.create_team(name)
    return JSONResponse({"message": "Team created successfully"}, status_code=status.HTTP_201_CREATED)
