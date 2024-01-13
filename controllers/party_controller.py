from core import ControllerAbstract
from .events import (
    JoinParty, SetPartyVideoUrl,
    SeekVideo
)
from type import WebSocket
import exceptions

class PartyController(ControllerAbstract):
    """The chat controller."""


    def check_if_auth(self, auth_token, user_id):
        print("1")
        if auth_token is None:
            raise exceptions.GeneralException(
                error_code=exceptions.ErrorCode.NOT_AUTH,
                message="YOU SHOULD LOGIN!"
            )
        
        print("2")
        auth_token_type, bearer_token = auth_token.split()
        if auth_token_type != "Bearer":
            raise exceptions.GeneralException(
                error_code=exceptions.ErrorCode.INVAILD_DATA,
                message="Not vaild data."
            )
        
        print("3")
        user_token_in_redis = self.redis_database.get_user_token(
            user_id=user_id
        )
        print(user_token_in_redis)
        if user_token_in_redis != bearer_token.encode():
            raise exceptions.GeneralException(
                error_code=exceptions.ErrorCode.NOT_AUTH,
                message="YOU SHOULD LOGIN!"
            )
        print("4")
        
    async def broadcast_to_party(self, party_id: int, **kwargs) -> None:
        """Broadcast message to the users in the room."""
        if party_id not in self.main_controller.parties_room.keys():
            raise exceptions.GeneralException(
                error_code=exceptions.ErrorCode.PARTY_NOT_FOUND,
                message="Party not found."
            )
        
        for websocket in self.main_controller.parties_room[party_id]:
            await websocket.send_json(kwargs)

    @ControllerAbstract.register_function(name="join_party")
    @ControllerAbstract.register_argument(name="party", type=JoinParty)
    async def join_party(self, event: JoinParty, ws: WebSocket):
        # When the user join the party
        # it going to emit this function
        # and it going to add the user
        # to the redis app

        self.check_if_auth(
            auth_token=ws.headers.get("Authorization"),
            user_id=event.user_id
        )
        
        if event.party_id not in self.main_controller.parties_room.keys():
            self.main_controller.parties_room[event.party_id] = []
        self.main_controller.parties_room[event.party_id].append(ws)
        self.main_controller.users_subed[ws] = event.user_id
        
        self.redis_database.add_user_to_party(
            event.party_id, user_id=event.user_id
        )

        await self.broadcast_to_party(
            party_id=event.party_id, event="user_joined",
            data={
                "user_id": event.user_id
            }
        )

    @ControllerAbstract.register_function("set_party_video_url")
    @ControllerAbstract.register_argument("update", SetPartyVideoUrl)
    async def on_set_party_video_url(self, event: "SetPartyVideoUrl", ws: WebSocket):
        # Just update the video url in the redis database
        # and then send a socket everywhere

        self.check_if_auth(
            auth_token=event.headers.get("Authorization"),
            user_id=event.user_id
        )

        if self.redis_database.check_if_user_in_party(
            party_id=event.party_id, user_id=event.user_id
        ) is False:
            raise exceptions.GeneralException(
                error_code=exceptions.ErrorCode.NOT_IN_PARTY,
                message="User not in party."
            )

        self.redis_database.set_party_video_url(
            event.party_id, event.video_url
        )
        await self.broadcast_to_party(
            party_id=event.party_id,
            event="update_party_video_url",
            data={
                "video_url": event.video_url
            }
        )

    @ControllerAbstract.register_function("update_video")
    @ControllerAbstract.register_argument("update", SeekVideo)
    async def on_update_video(self, event: "SeekVideo", ws: WebSocket):
        # Sekk the video.

        x = self.check_if_auth(
            auth_token=ws.headers.get("Authorization"),
            user_id=event.user_id
        )

        if self.redis_database.check_if_user_in_party(
            party_id=event.party_id, user_id=event.user_id
        ) is False:
            raise exceptions.GeneralException(
                error_code=exceptions.ErrorCode.NOT_IN_PARTY,
                message="User not in party."
            )

        await self.broadcast_to_party(
            party_id=event.party_id,
            event="seek_to",
            data={
                "state": event.state,
                "seek_to": event.seek_to
            }
        )