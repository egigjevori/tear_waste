from __future__ import annotations

import enum

import bcrypt


class UserRole(enum.Enum):
    EMPLOYEE = "Employee"
    MANAGER = "Manager"
    ADMIN = "Admin"


def _hash_password(password):
    """Hash the user's password."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


class User:
    def __init__(self, username: str, email: str, role: UserRole, password_hash: str | None = None, id: int | None = None):
        self.id = id  # ID would typically be set by the database
        self.username = username
        self.email = email
        self.role = role
        self.password_hash = password_hash

    def set_password(self, password):
        """Hash and set the user's password."""
        self.password_hash = _hash_password(password)

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}', role='{self.role}')>"
