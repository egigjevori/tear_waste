from fastapi import Body
from starlette import status
from starlette.responses import JSONResponse

from app.services import team_service
from fastapi import APIRouter

team_router = APIRouter()


@team_router.post("/teams")
async def create_team(name: str = Body(...)) -> JSONResponse:
    await team_service.create_team(name)
    return JSONResponse({"message": "Team created successfully"}, status_code=status.HTTP_201_CREATED)
