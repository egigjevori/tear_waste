# file: tests/test_authorization_service.py

import pytest
from unittest.mock import AsyncMock, patch

from app.models.users import User, UserRole
from app.services.authorization_service import verify_authorization, AuthorizationError
from app.utils.permissions import Permission


@pytest.fixture
def mock_user_service():
    with patch("app.services.authorization_service.user_service", return_value=AsyncMock()) as mock:
        mock.get_users_by_team_id = AsyncMock(
            return_value=[
                User(id=2, role=UserRole.EMPLOYEE, team_id=1, username="test", email="<EMAIL>"),
                User(id=3, role=UserRole.EMPLOYEE, team_id=1, username="test", email="<EMAIL>"),
            ]
        )
        yield


async def test_employee_permission_granted():
    user = User(id=1, role=UserRole.EMPLOYEE, team_id=1, username="test", email="<EMAIL>")
    request_data = {"user_id": 1}
    await verify_authorization(user, Permission.GET_WASTE_BY_USER_ID, request_data)


async def test_employee_permission_denied():
    user = User(id=1, role=UserRole.EMPLOYEE, team_id=1, username="test", email="<EMAIL>")
    request_data = {"user_id": 2}
    with pytest.raises(AuthorizationError):
        await verify_authorization(user, Permission.GET_WASTE_BY_USER_ID, request_data)


async def test_manager_permission_granted(mock_user_service):
    user = User(id=1, role=UserRole.MANAGER, team_id=1, username="test", email="<EMAIL>")
    request_data = {"user_id": 2}
    await verify_authorization(user, Permission.GET_WASTE_BY_USER_ID, request_data)


async def test_manager_permission_denied(mock_user_service):
    user = User(id=1, role=UserRole.MANAGER, team_id=1, username="test", email="<EMAIL>")
    request_data = {"user_id": 4}  # User ID not in the team
    with pytest.raises(AuthorizationError):
        await verify_authorization(user, Permission.GET_WASTE_BY_USER_ID, request_data)


async def test_manager_team_permission_granted():
    user = User(id=1, role=UserRole.MANAGER, team_id=1, username="test", email="<EMAIL>")
    request_data = {"team_id": 1}
    await verify_authorization(user, Permission.GET_WASTE_BY_TEAM_ID, request_data)


async def test_manager_team_permission_denied():
    user = User(id=1, role=UserRole.MANAGER, team_id=1, username="test", email="<EMAIL>")
    request_data = {"team_id": 2}  # Different team ID
    with pytest.raises(AuthorizationError):
        await verify_authorization(user, Permission.GET_WASTE_BY_TEAM_ID, request_data)


async def test_admin_permission_granted():
    user = User(id=1, role=UserRole.ADMIN, team_id=1, username="test", email="<EMAIL>")
    request_data = {"user_id": 1}
    await verify_authorization(user, Permission.CREATE_USER, request_data)
