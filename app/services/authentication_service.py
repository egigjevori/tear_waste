import time

from starlette.responses import JSONResponse

from app.models.users import User
from app.services import user_service
from app.utils.jwt import create_jwt
from app.utils.password import hash_password, verify_password


class AuthenticationError(Exception):
    pass


def create_token(user: User) -> str:
    payload = {
        "sub": user.id,
        "exp": int(time.time()) + (3600 * 24 * 30),  # Expires in 30 days
        "iat": int(time.time()),

        "role": user.role.value,
        "username": user.username,
        "email": user.email,
        "team_id": user.team_id
    }
    token = create_jwt(payload)
    return token


async def authenticate(username: str, password: str) -> str:
    user = await user_service.get_user_by_username(username)
    if not user:
        raise AuthenticationError(f"User {username} not found")
    if not verify_password(password, user.password_hash):
        raise AuthenticationError(f"Wrong password")

    token = create_token(user)
    return token