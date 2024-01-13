from enum import Enum, auto
from typing import (
    Optional
)

class ErrorCode(Enum):
    """For each error there is an
    error code so the frontend
    developer can clearfiy the
    error"""

    NO_EVENT_FOUND = auto()
    INVAILD_DATA = auto()
    WRONG_DATA = auto()
    USER_ALREADY_IN_PARTY = auto()
    PARTY_NOT_FOUND = auto()
    CONTROLLER_NOT_FOUND = auto()
    EVENT_NOT_FOUND = auto()
    NOT_AUTH = auto()
    NOT_IN_PARTY = auto()

class ExceptionAbstract(Exception):
    """Base abstraction to the errors."""
    def __init__(
        self, 
        error_code: int, 
        message: Optional[str]
    ):
        self.error_code = error_code
        self.message = message

        super().__init__(message)

class GeneralException(ExceptionAbstract):
    pass