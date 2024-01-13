import tinyws
import tinyws.server
import uvicorn
import secrets
import uvloop

from core import (
    ControllerManager, RedisDatabaseManager
)
from controllers import (
    PartyController, ChatController
)

redis_database = RedisDatabaseManager(
    database_host="172.20.10.6",
    database_port=6379
)
party_controller = PartyController("/party")
chat_controller = ChatController("/chat")
controller = ControllerManager(
    controllers=[
        party_controller,
        chat_controller
    ],
    redis_database=redis_database
)
    

websocket_per_token = {}

@tinyws.server.app()
async def application(websocket: tinyws.WebSocket) -> None:
    """The main handler of the application."""
    await websocket.accept()

    token_for_socket = secrets.token_hex(6)
    websocket_per_token[token_for_socket] = websocket

    while True:
        try:
            # read the data.
            await controller.on_request(websocket)
        except Exception as e:
            await controller.on_disconnect(websocket)
            raise e

uvloop.install()
uvicorn.run(
    app=application,
    ws="wsproto",
)