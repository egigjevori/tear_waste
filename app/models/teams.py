from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Team:
    def __init__(self, name: str, id: int | None = None):
        self.name = name
        self.id = id

    def to_dict(self) -> dict:
        """Convert the Team instance to a dictionary."""
        return {
            'name': self.name,
            'id': self.id
        }

    @classmethod
    def from_dict(cls, data: dict) -> Team:
        """Create a Team instance from a dictionary."""
        return cls(
            name=data.get('name'),
            id=data.get('id')
        )
