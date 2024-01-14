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

    @ControllerAbstract.register_function("create_message")
    @ControllerAbstract.register_argument(name="message", type=CreateMessage)
    async def create_message(self, event: CreateMessage, ws: WebSocket) -> None:
        self.main_controller.check_if_auth(
            websocket=ws,
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
                "content": event.content,
                "party_id": event.party_id
            }
        )