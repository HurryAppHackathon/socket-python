from core import (
    ControllerAbstract, MessageObject
)
from .events import (
    CreateMessage
)
from type import WebSocket
import exceptions
import datetime

class ChatController(ControllerAbstract):
    """The chat controller."""

    chats = {}

    def check_if_auth(self, auth_token, user_id):
        auth_token = auth_token
        if auth_token is None:
            raise exceptions.GeneralException(
                error_code=exceptions.ErrorCode.NOT_AUTH,
                message="YOU SHOULD LOGIN!"
            )
        
        auth_token_type, bearer_token = auth_token.split()
        if auth_token_type != "Bearer":
            raise exceptions.GeneralException(
                error_code=exceptions.ErrorCode.INVAILD_DATA,
                message="Not vaild data."
            )
        
        user_token_in_redis = self.redis_database.get_user_token(
            user_id=user_id
        )
        if user_token_in_redis != bearer_token.encode():
            raise exceptions.GeneralException(
                error_code=exceptions.ErrorCode.NOT_AUTH,
                message="YOU SHOULD LOGIN!"
            )

    async def broadcast_to_party(self, party_id: int, **kwargs) -> None:
        """Broadcast message to the users in the room."""
        if party_id not in self.main_controller.parties_room.keys():
            raise exceptions.GeneralException(
                error_code=exceptions.ErrorCode.PARTY_NOT_FOUND,
                message="Party not found."
            )
        
        for websocket in self.main_controller.parties_room[party_id]:
            await websocket.send_json(kwargs)

    @ControllerAbstract.register_function("create_message")
    @ControllerAbstract.register_argument(name="message", type=CreateMessage)
    async def create_message(self, event: CreateMessage, ws: WebSocket) -> None:
        self.check_if_auth(
            auth_token=ws.headers.get("Authorization"),
            user_id=event.user_id
        )

        self.redis_database.check_if_user_in_party(
            party_id=event.party_id,
            user_id=event.user_id
        )

        message_obj = MessageObject(
            id=None,
            content=event.content,
            party_id=event.party_id,
            user_id=event.user_id,
            timestamp=datetime.datetime.now()
        )
        if event.party_id not in self.chats.keys():
            self.chats[event.party_id] = []

        self.chats[event.party_id].append(message_obj)
        await self.broadcast_to_party(
            party_id=event.party_id,
            event="chat_sent",
            data={
                "user_id": event.user_id,
                "message": event.content,
                "party_id": event.party_id
            }
        )