from typing import (
    Optional, Literal
)
from core import BaseObject
import dataclasses

@dataclasses.dataclass
class JoinParty(BaseObject):
    party_id: int
    user_id: int
    invite_code: Optional[str] = None

@dataclasses.dataclass
class SetPartyVideoUrl(BaseObject):
    party_id: int
    video_url: str
    user_id: int

@dataclasses.dataclass
class SeekVideo(BaseObject):
    party_id: int
    user_id: int
    state: Literal["mute", "pause", "start"]
    seek_to: int