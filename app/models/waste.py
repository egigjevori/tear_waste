from __future__ import annotations

from datetime import datetime

class WasteEntry:
    def __init__(self, type: str, weight: float, user_id: int, id: int | None = None, timestamp: datetime = datetime.now()):
        self.id = id
        self.type = type
        self.weight = weight
        self.timestamp = timestamp
        self.user_id = user_id

    def __repr__(self):
        return (f"WasteEntry(id={self.id}, type='{self.type}', weight={self.weight}, "
                f"timestamp={self.timestamp}, user_id={self.user_id})")