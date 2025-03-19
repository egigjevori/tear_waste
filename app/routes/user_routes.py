

from fastapi import Body
from starlette import status
from starlette.responses import JSONResponse

from app.services import team_service, user_service
from fastapi import APIRouter

user_router = APIRouter()

@user_router.post("/users")
async def create_user(
        username: str = Body(...),
        email: str = Body(...),
        role: str = Body(...),
        team_id: int = Body(...),
        password: str = Body(...),
) -> JSONResponse:
    user = await user_service.create_user(username, email, role, team_id, password)
    return JSONResponse(
        {"message": "User created successfully"}, status_code=status.HTTP_201_CREATED
    )
