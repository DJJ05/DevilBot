# -*- coding: utf-8 -*-

from motor.motor_asyncio import AsyncIOMotorClient

from .secrets import secrets_mongo_uri, secrets_mongo_dbname


class mongo:
    """Database connection commands"""

    def __init__(self, loop):
        self.db_conn = AsyncIOMotorClient(
            secrets_mongo_uri,
            io_loop=loop
        )[secrets_mongo_dbname]
        self.logging = self.db_conn["Logging"]
        self.starboard = self.db_conn["Starboard"]
        self.starboard_config = self.db_conn["Starboard_config"]
