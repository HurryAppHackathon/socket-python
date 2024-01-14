from core import BaseObject
import dataclasses
import datetime

@dataclasses.dataclass
class CreateMessage(BaseObject):
    content: str
    party_id: int
    user_id: int
    ser_id: int = None
    timestamp: datetime.datetime = datetime.datetime.now()