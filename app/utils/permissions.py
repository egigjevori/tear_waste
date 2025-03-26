import enum
from typing import List

from app.models.users import UserRole


class Permission(enum.Enum):
    # Waste routes
    CREATE_WASTE = "create_waste"
    GET_WASTE_BY_USER_ID = "get_waste_by_user_id"

    # User routes
    CREATE_USER = "create_user"
    GET_USERS_BY_TEAM_ID = "get_users_by_team_id"

    # Team routes
    CREATE_TEAM = "create_team"


EMPLOYEE_PERMISSIONS: List[Permission] = [
    Permission.CREATE_WASTE,
    Permission.GET_WASTE_BY_USER_ID,
]

MANAGER_PERMISSIONS: List[Permission] = [
    Permission.CREATE_WASTE,
    Permission.GET_WASTE_BY_USER_ID,
    Permission.GET_USERS_BY_TEAM_ID,
]

ADMIN_PERMISSIONS: List[Permission] = list(Permission)

ROLE_PERMISSIONS = {
    UserRole.ADMIN: ADMIN_PERMISSIONS,
    UserRole.MANAGER: MANAGER_PERMISSIONS,
    UserRole.EMPLOYEE: EMPLOYEE_PERMISSIONS,
}
