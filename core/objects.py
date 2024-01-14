from dataclasses import dataclass
from typing import (
    List, Dict, Optional
)
import datetime

@dataclass
class BaseObject:
    pass

@dataclass
class UserObject:
    id: int
    username: str
    email: str
    created_at: datetime.datetime

@dataclass
class PartyObject:
    id: int
    user_id: int
    video_url: str
    invite_url: str

@dataclass
class MessageObject:
    id: int
    content: str
    party_id: int
    user_id: int
    timestamp: datetime.date