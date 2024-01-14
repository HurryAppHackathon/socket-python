from typing import (
    Optional, Dict, List
)
from .objects import (
    UserObject
)
import exceptions
import psycopg2
import redis

class RedisDatabaseManager:
    """A manager for the database, it mission
    is to add and retreive data and parse it
    into an object and methods to add, delete and
    update data."""

    def __init__(
        self,
        database_host: str,
        database_port: int,
        node: Optional[int] = None
    ) -> None:
        self.redis_instance = redis.Redis(
            host=database_host,
            port=database_port
        )
        self.postgress_database: "PostgressDatabaseManager" = None
        self.node = node

    def set_party_video_url(self, party_id: int, video_url: str) -> bool:
        """Set the party_video."""
        
        if self.redis_instance.exists(f"parties:{party_id}") == 0:
            raise exceptions.GeneralException(
                error_code=exceptions.ErrorCode.PARTY_NOT_FOUND,
                message="Party not found"
            )
        
        return self.redis_instance.hset(
            f"parties:{party_id}", "video_url", video_url
        )

    def get_party(self, party_id: int) -> Dict[bytes, bytes]:
        """Get the video id."""

        if self.redis_instance.exists(f"parties:{party_id}") == 0:
            raise exceptions.GeneralException(
                error_code=exceptions.ErrorCode.PARTY_NOT_FOUND,
                message="Party not found"
            )
        
        return self.redis_instance.hgetall(f"parties:{party_id}")
    
    def get_party_id(self, invite_code: str) -> str:
        """Get the party id via token."""

        party_id = self.redis_instance.get(
            name=f"invite_codes:{invite_code}"
        )
        return int(party_id)
    
    def get_users_in_party(self, party_id: int) -> List:
        """Get all the members in the party."""
        if self.redis_instance.exists(f"parties:{party_id}") == 0:
            raise exceptions.GeneralException(
                error_code=exceptions.ErrorCode.PARTY_NOT_FOUND,
                message="Party not found"
            )
        
        return self.redis_instance.lrange(f"parties_users:{party_id}", 0, -1)

    def check_if_user_in_party(self, party_id: str, user_id: int) -> bool:
        """Checks if the user in the party."""
        if self.redis_instance.exists(f"parties:{party_id}") == 0:
            raise exceptions.GeneralException(
                error_code=exceptions.ErrorCode.PARTY_NOT_FOUND,
                message="Party not found"
            )
        
        party_users = self.redis_instance.lrange(f"parties_users:{party_id}", 0, -1)
        if str(user_id).encode() in party_users:
            return True
        
        return False

    def add_user_to_party(self, party_id: str, user_id: int) -> bool:
        """Add user to a party."""
        if self.check_if_user_in_party(party_id, user_id) is True:
            raise exceptions.GeneralException(
                error_code=exceptions.ErrorCode.USER_ALREADY_IN_PARTY,
                message="User is already in a party"
            )

        self.redis_instance.set(f"user_sub_to:{user_id}", party_id)
        return self.redis_instance.lpush(
            f"parties_users:{party_id}", user_id
        )
    
    def add_user_to_disconnect_users(self, party_id: str, user_id: int) -> bool:
        """When user disconnect, it have to be added to the
        disconnected users so that we can notify them when they come back."""

        if self.redis_instance.exists(f"parties_users:{party_id}") is False:
            raise exceptions.GeneralException(
                error_code=exceptions.ErrorCode.PARTY_NOT_FOUND,
                message="Party not found"
            )

        return self.redis_instance.set(
            f"disconnected_users:{user_id}", party_id
        )
    
    def get_user_token(self, user_id: int) -> bool:
        """Get the user token."""
        if self.redis_instance.exists(f"tokens:{user_id}") is False:
            raise exceptions.GeneralException(
                error_code=exceptions.ErrorCode.NOT_AUTH,
                message="User not logined."
            )
        
        return self.redis_instance.get(f"tokens:{user_id}")
    
    def remove_user_from_party(self, party_id: int, user_id: int) -> bool:
        """Remove the user from the party."""
        if self.check_if_user_in_party(party_id, user_id) is False:
            raise exceptions.GeneralException(
                error_code=exceptions.ErrorCode.NOT_IN_PARTY,
                message="User not in party."
            )
        
        self.redis_instance.lrem(
            f"parties_users:{party_id}", 1, str(user_id).encode("utf-8")
        )
        
    def set_database(self, database: "PostgressDatabaseManager") -> None:
        """Set the database."""
        self.postgress_database = database

class PostgressDatabaseManager:
    """A manager for the postgress database
    so we can get the things from it."""

    def __init__(
        self,
        host: str,
        port: int,
        user: str,
        password: str
    ) -> None:
        self.postgress_database = psycopg2.connect(
            database="streaming_service_backend",
            host=host,
            port=port,
            user=user,
            password=password
        )
        self.postgress_cursor = self.postgress_database.cursor()

    def get_user(self, user_id: int) -> "UserObject":
        """Fetch the user."""
        QUERY = f'SELECT * FROM "public".users where id = {user_id}'
        self.postgress_cursor.execute(QUERY)

        user_data = self.postgress_cursor.fetchone()
        user_object = UserObject(
            id=user_data[0],
            username=user_data[1],
            email=user_data[4],
            created_at=user_data[-2]
        )
        return user_object
    
    def get_user(self, user_id: int) -> "UserObject":
        """Fetch the user."""
        QUERY = f'SELECT * FROM "public".users where id = {user_id}'
        self.postgress_cursor.execute(QUERY)

        user_data = self.postgress_cursor.fetchone()
        user_object = UserObject(
            id=user_data[0],
            username=user_data[1],
            email=user_data[4],
            created_at=user_data[-2]
        )
        return user_object