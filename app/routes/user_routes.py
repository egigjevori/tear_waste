from dataclasses import asdict
from typing import List

from fastapi import Body, HTTPException
from starlette import status
from starlette.responses import JSONResponse

from app.models.users import User
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
    return JSONResponse({"message": "User created successfully"}, status_code=status.HTTP_201_CREATED)


@user_router.get("/users/by-team/{team_id}")
async def get_users_by_team_id(team_id: int):
    try:
        users = await user_service.get_users_by_team_id(team_id=team_id)
        users = [
            {
                "username": user.username,
                "email": user.email,
                "role": user.role.value,
                "team_id": user.team_id,
            }
            for user in users
        ]
        return JSONResponse(users, status_code=status.HTTP_200_OK)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
