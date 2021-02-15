# -*- coding: utf-8 -*-

from motor.motor_asyncio import AsyncIOMotorClient

from secrets import mongo_uri, mongo_dbname


class mongo:
    def __init__(self, loop):
        self.db_conn = AsyncIOMotorClient(
            mongo_uri,
            io_loop=loop
        )[mongo_dbname]
        self.logging = self.db_conn["Logging"]
        self.starboard = self.db_conn["Starboard"]
        self.starboard_config = self.db_conn["Starboard_config"]
