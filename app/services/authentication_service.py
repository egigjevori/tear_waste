import functools
import time

from starlette.responses import JSONResponse

from app.models.users import User, UserRole
from app.services import user_service
from app.utils.jwt import create_jwt, verify_jwt, JWTError
from app.utils.password import hash_password, verify_password
from app.utils.permissions import Permission


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


async def verify_authentication(token: str) -> User:
    if not token or not token.startswith("Bearer "):
        raise AuthenticationError("Invalid or missing Authorization header")
    token = token.removeprefix("Bearer ").strip()
    try:
        payload = verify_jwt(token)
        user = User(
            id=payload["sub"],
            username=payload["username"],
            email=payload["email"],
            team_id=payload["team_id"],
            role=UserRole(payload["role"]),
        )
        return user
    except JWTError as e:
        raise AuthenticationError(str(e))
