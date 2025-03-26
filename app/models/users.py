from __future__ import annotations

import enum
from dataclasses import dataclass

from app.utils.password import hash_password


class UserRole(enum.Enum):
    EMPLOYEE = "Employee"
    MANAGER = "Manager"
    ADMIN = "Admin"


@dataclass
class User:
    def __init__(
        self,
        username: str,
        email: str,
        role: UserRole,
        team_id: int,
        password_hash: str | None = None,
        id: int | None = None,
    ):
        self.id = id  # ID would typically be set by the database
        self.username = username
        self.email = email
        self.role = role
        self.team_id = team_id
        self.password_hash = password_hash

    def set_password(self, password):
        """Hash and set the user's password."""
        self.password_hash = hash_password(password)

    def to_dict(self, sensitive=False) -> dict:
        """Convert the User instance to a dictionary."""
        data= {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role.value,  # Convert enum to its value
            'team_id': self.team_id,
        }
        if not sensitive:
            data['password_hash'] = self.password_hash
        return data

    @classmethod
    def from_dict(cls, data: dict) -> User:
        """Create a User instance from a dictionary."""
        return cls(
            id=data.get('id'),
            username=data['username'],
            email=data['email'],
            role=UserRole(data['role']),  # Convert string to UserRole enum
            team_id=data['team_id'],
            password_hash=data.get('password_hash')  # Handle optional password_hash
        )
