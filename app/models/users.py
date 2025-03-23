from __future__ import annotations

import enum
from dataclasses import dataclass

import bcrypt

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

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}', role='{self.role}')>"
