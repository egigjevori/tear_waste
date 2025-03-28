import logging
from functools import wraps
from typing import Callable

from fastapi import Request

from app.models.users import User, UserRole
from app.services import authentication_service, user_service
from app.utils.permissions import ROLE_PERMISSIONS, Permission

logger = logging.getLogger(__name__)


class AuthorizationError(Exception):
    pass


def verify(assertion: bool, message: str):
    if not assertion:
        logger.warning(f"Authorization verification failed: {message}")
        raise AuthorizationError(message)


async def verify_authorization(current_user: User, permission: Permission, request_data: dict):
    logger.info(
        f"Verifying authorization for user {current_user.id} with role {current_user.role.value} for permission {permission}"
    )

    user_permissions = ROLE_PERMISSIONS[current_user.role]
    if permission not in user_permissions:
        logger.warning(f"User {current_user.id} does not have permission to {permission}")
        raise AuthorizationError(
            f"User {current_user.id}, role {current_user.role.value} does not have permission to {permission}"
        )

    if current_user.role == UserRole.EMPLOYEE:
        # custom Employee authorization logic
        if permission == Permission.GET_WASTE_BY_USER_ID:
            request_user_id = request_data["user_id"]
            verify(
                request_user_id == current_user.id,
                f"User {current_user.id} does not have access to user {request_user_id}",
            )

    if current_user.role == UserRole.MANAGER:
        # custom Manager authorization logic
        if permission == Permission.GET_WASTE_BY_USER_ID:
            request_user_id = request_data["user_id"]
            team_users = await user_service.get_users_by_team_id(current_user.team_id)
            verify(
                request_user_id in [u.id for u in team_users],
                f"User {current_user.id} does not have access to user {request_user_id}",
            )

        if permission == Permission.GET_USERS_BY_TEAM_ID:
            request_team_id = request_data["team_id"]
            verify(
                request_team_id == current_user.team_id,
                f"User {current_user.id} is not the manager of {request_team_id}",
            )

    logger.info(f"Authorization verified for user {current_user.id} with permission {permission}")


def require_permission(required_permission: Permission):
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request: Request = kwargs.get("request")
            if "Authorization" not in request.headers:
                raise AuthorizationError("No authorization header provided")
            token = request.headers.get("Authorization")
            user = await authentication_service.verify_authentication(token)
            logger.info(f"User authenticated: {user}")
            await verify_authorization(user, required_permission, kwargs)
            return await func(*args, **kwargs)

        return wrapper

    return decorator
