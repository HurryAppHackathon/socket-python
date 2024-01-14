import tinyws
import tinyws.server
import uvicorn
import uvloop

from core import (
    ControllerManager, RedisDatabaseManager,
    PostgressDatabaseManager
)
from exceptions import GeneralException
from controllers import (
    PartyController, ChatController,
)
from dotenv import dotenv_values

env = dotenv_values()
redis_database = RedisDatabaseManager(
    database_host=env["REDIS_HOST"],
    database_port=env["REDIS_PORT"]
)
postgress_database = PostgressDatabaseManager(
    host=env["POSTGRESS_HOST"],
    port=env["POSTGRESS_PORT"],
    POSTGRESS_USERNAME=env["POSTGRESS_USERNAME"],
    password=env["POSTGRESS_PASSWORD"]
)
redis_database.set_database(postgress_database)

party_controller = PartyController("/party")
chat_controller = ChatController("/chat")
controller = ControllerManager(
    controllers=[
        party_controller,
        chat_controller,
    ],
    redis_database=redis_database
)

@tinyws.server.app()
async def application(websocket: tinyws.WebSocket) -> None:
    """The main handler of the application."""
    await websocket.accept()

    while True:
        try:
            # read the data.
            await controller.on_request(websocket)
        except Exception as e:
            if issubclass(e.__class__, (GeneralException, )):
                print(e)
                await websocket.send_json(
                    e.json_error()
                )
            else:
                await controller.on_disconnect(websocket)
                break


uvloop.install()
uvicorn.run(
    app=application,
    ws="wsproto",
)