from __future__ import annotations

import time

from app.models.users import User, UserRole
from app.services import user_service
from app.utils.jwt import JWTError, create_jwt, verify_jwt
from app.utils.password import verify_password


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
        "team_id": user.team_id,
    }
    token = create_jwt(payload)
    return token


async def authenticate(username: str, password: str) -> str:
    user = await user_service.get_user_by_username(username)
    if not user:
        raise AuthenticationError(f"User {username} not found")
    if not verify_password(password, user.password_hash):  # type: ignore
        raise AuthenticationError("Wrong password")

    token = create_token(user)
    return token


async def verify_authentication(token: str | None) -> User:
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
