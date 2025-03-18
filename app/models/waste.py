from datetime import datetime

class WasteEntry:
    def __init__(self, id: int, type: str, weight: float, timestamp: datetime, user_id: int, team_id: int):
        self.id = id
        self.type = type
        self.weight = weight
        self.timestamp = timestamp
        self.user_id = user_id

    def __repr__(self):
        return (f"WasteEntry(id={self.id}, type='{self.type}', weight={self.weight}, "
                f"timestamp={self.timestamp}, user_id={self.user_id})")