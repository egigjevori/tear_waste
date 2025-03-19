from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Team:
    def __init__(self, name: str, id: int | None = None):
        self.name = name
        self.id = id

    def __repr__(self):
        return f"Team(id={self.id}, name='{self.name}')"
