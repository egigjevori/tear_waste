import logging
from fastapi import APIRouter, Body, Request
from starlette import status
from starlette.responses import JSONResponse

from app.services import authorization_service, user_service
from app.utils.permissions import Permission

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

user_router = APIRouter()


@user_router.post("/users")
@authorization_service.require_permission(Permission.CREATE_USER)
async def create_user(
    _: Request,
    username: str = Body(...),
    email: str = Body(...),
    role: str = Body(...),
    team_id: int = Body(...),
    password: str = Body(...),
) -> JSONResponse:
    logger.info(
        f"Attempting to create user with username: {username}, email: {email}, role: {role}, team_id: {team_id}"
    )

    await user_service.create_user(username, email, role, team_id, password)

    logger.info(f"User '{username}' created successfully")
    return JSONResponse({"message": "User created successfully"}, status_code=status.HTTP_201_CREATED)


@user_router.get("/users/by-team/{team_id}")
@authorization_service.require_permission(Permission.GET_USERS_BY_TEAM_ID)
async def get_users_by_team_id(_: Request, team_id: int):
    logger.info(f"Fetching users for team_id: {team_id}")

    users = await user_service.get_users_by_team_id(team_id=team_id)

    logger.info(f"Found {len(users)} users for team_id: {team_id}")

    users_dict = [
        {
            "username": user.username,
            "email": user.email,
            "role": user.role.value,
            "team_id": user.team_id,
        }
        for user in users
    ]
    return JSONResponse(users_dict, status_code=status.HTTP_200_OK)
