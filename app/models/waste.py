from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class WasteEntry:
    def __init__(
        self,
        type: str,
        weight: float,
        user_id: int,
        id: int | None = None,
        timestamp: datetime = datetime.now(),
    ):
        self.id = id
        self.type = type
        self.weight = weight
        self.timestamp = timestamp
        self.user_id = user_id

    def to_dict(self) -> dict:
        """Convert the WasteEntry instance to a dictionary."""
        return {
            'id': self.id,
            'type': self.type,
            'weight': self.weight,
            'timestamp': self.timestamp.isoformat(),  # Convert datetime to ISO format string
            'user_id': self.user_id
        }

    @classmethod
    def from_dict(cls, data: dict) -> WasteEntry:
        """Create a WasteEntry instance from a dictionary."""
        timestamp = datetime.fromisoformat(data['timestamp']) if isinstance(data['timestamp'], str) else data['timestamp']
        return cls(
            id=data.get('id'),
            type=data['type'],
            weight=data['weight'],
            timestamp=timestamp,  # Convert ISO format string to datetime
            user_id=data['user_id']
        )