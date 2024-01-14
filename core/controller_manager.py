from typing import (
    Optional, Dict, List
)
from .objects import BaseObject
from .database_manager import (
    RedisDatabaseManager, PostgressDatabaseManager
)

import exceptions
import dataclasses
import tinyws

@dataclasses.dataclass
class FunctionEvent:
    """The event object"""
    name: Optional[str] = None
    callback: Optional[callable] = None

function_per_controller = {

}

class ControllerAbstract:
    events: Dict[str, FunctionEvent] = {}

    def __init__(
        self,
        name: str,
        before_request: Optional[callable] = None,
    ) -> None:
        """Make the inital class for the
        controller."""
        self.name = name
        self.before_request = before_request
        self.redis_database: "RedisDatabaseManager" = None
        self.postgress_database: "PostgressDatabaseManager" = None
        self.main_controller: "ControllerManager" = None

    @classmethod 
    def register_function(
        cls: "ControllerAbstract",
        name: str,
    ) -> callable:
        """Register the function to the controller.
        
        Args:
            - name: The name of the event will
            be emitted.
        """

        def decorator(function: callable):
            event = FunctionEvent(
                name=name,
                callback=function,
            )

            cls.events[name] = event
                
            return function
        
        return decorator
    
    @staticmethod
    def register_argument(
        name: str,
        type: BaseObject
    ) -> callable:
        """Register a new argument."""

        def decorator(function: callable):
            if getattr(function, "controller_args", None) is None:
                setattr(function, "controller_args", {})

            function.controller_args[name] = type
            return function
        
        return decorator

    async def trigger_function(self, name: str, websocket_instance: tinyws.WebSocket, websocket_data) -> None:
        """Find the function and trigger it from"""

        event_function = self.events.get(name, None)
        if event_function is None:
            raise exceptions.GeneralException(
                error_code=exceptions.ErrorCode.NO_EVENT_FOUND,
                message="No Function Found"
            )

        
        if self.before_request is not None:
            try:
                resp = await self.before_request(
                    websocket_instance,
                )
                return await self.websocket_instance.send(resp)
            except Exception as exception:
                raise exception
        
        if "data" not in websocket_data.keys():
            raise exceptions.GeneralException(
                error_code=exceptions.ErrorCode.INVAILD_DATA,
                message="Invaild data packet."
            )
        
        args = []
        callback = event_function.callback
        for name in websocket_data.get("data").keys():
            if name in callback.controller_args.keys():
                converted_object = callback.controller_args.get(name)
                try:
                    args.append(
                        converted_object( 
                            **websocket_data.get("data")[name],
                        )
                    )
                except:
                    raise exceptions.GeneralException(
                        error_code=exceptions.ErrorCode.INVAILD_DATA,
                        message="Not vaild data."
                    )

        token_value = websocket_data.get('token', None)
        if token_value is None:
            raise exceptions.GeneralException(
                error_code=exceptions.ErrorCode.NOT_AUTH,
                message="No token found."
            )
        
        if getattr(websocket_instance, "token", None) is None:
            setattr(websocket_instance, "token", token_value)
        
        if len(args) != 0:
            await callback(self, *args, websocket_instance)
        else:
            await callback(self, websocket_instance)

class ControllerManager:
    """When the request hits the controller it
    will see which controller the request is for
    and then emit the functino there."""
    def __init__(
        self,
        controllers: List["ControllerAbstract"],
        redis_database: "RedisDatabaseManager",
    ) -> None:
        self.controllers: Dict[str, "ControllerAbstract"] = {}
        self.redis_database = redis_database
        self.parties_room: Dict[str, List["tinyws.WebSocket"]] = {}
        self.users_subed = {}
        for controller in controllers:
            controller.redis_database = redis_database
            controller.main_controller = self
            self.controllers[controller.name] = controller

    def check_if_auth(self, websocket: tinyws.WebSocket, user_id: int) -> None:
        """Check if the user is auth."""
        if hasattr(websocket, "token") is False:
            raise exceptions.GeneralException(
                error_code=exceptions.ErrorCode.NOT_AUTH,
                message="DO Auth Someone"
            )

        auth_token = websocket.token
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
        if party_id not in self.parties_room.keys():
            raise exceptions.GeneralException(
                error_code=exceptions.ErrorCode.PARTY_NOT_FOUND,
                message="Party not found."
            )
        
        for websocket in self.parties_room[party_id]:
            await websocket.send_json(kwargs)

    async def on_request(self, websocket_instance: tinyws.WebSocket) -> None:
        """It going to find which controller it trys to speak
        to and then trigger the function."""
        data = await websocket_instance.receive_json()
        controller_path, event = data["controller"], data["event"]
        
        controller = self.controllers.get(
            controller_path, None
        )
        
        if controller is None:
            raise exceptions.GeneralException(
                error_code=exceptions.ErrorCode.CONTROLLER_NOT_FOUND,
                message="Controller not found."
            )
        
        await controller.trigger_function(event, websocket_instance, data)

    async def on_disconnect(self, websocket_instance: tinyws.WebSocket) -> None:
        """When the websocket disconnect it's going to do this."""

        user_id = self.users_subed.get(websocket_instance, None)
        if user_id is None:
            return False
        
        party_subed_to = self.redis_database.redis_instance.get(
            f"user_sub_to:{user_id}"
        )
        party_subed_to = int(party_subed_to)
        self.redis_database.remove_user_from_party(
            party_subed_to, user_id
        )
        self.parties_room[party_subed_to].remove(websocket_instance)
        self.users_subed.pop(websocket_instance)