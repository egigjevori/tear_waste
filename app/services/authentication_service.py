from __future__ import annotations

import logging
import time

from app.models.users import User, UserRole
from app.services import user_service
from app.utils.jwt import JWTError, create_jwt, verify_jwt
from app.utils.password import verify_password

logger = logging.getLogger(__name__)


class AuthenticationError(Exception):
    pass


def create_token(user: User) -> str:
    logger.info(f"Creating token for user: {user.username}")

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

    logger.info(f"Token created for user: {user.username}")
    return token


async def authenticate(username: str, password: str) -> str:
    logger.info(f"Authenticating user: {username}")

    user = await user_service.get_user_by_username(username)
    if not user:
        logger.warning(f"Authentication failed: User {username} not found")
        raise AuthenticationError(f"User {username} not found")

    if not verify_password(password, user.password_hash):  # type: ignore
        logger.warning(f"Authentication failed: Wrong password for user {username}")
        raise AuthenticationError("Wrong password")

    token = create_token(user)

    logger.info(f"User {username} authenticated successfully")
    return token


async def verify_authentication(token: str | None) -> User:
    logger.info("Verifying authentication token")

    if not token or not token.startswith("Bearer "):
        logger.warning("Invalid or missing Authorization header")
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

        logger.info(f"Token verified for user: {user.username}")
        return user
    except JWTError as e:
        logger.error(f"Token verification failed: {str(e)}")
        raise AuthenticationError(str(e))
