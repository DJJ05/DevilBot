# -*- coding: utf-8 -*-

from motor.motor_asyncio import AsyncIOMotorClient
from discord.ext import commands

from .secrets import secrets_mongo_uri, secrets_mongo_dbname


class mongoCog(commands.Cog):
    """Database connection commands"""

    def __init__(self, bot):
        self.bot = bot
        self.colour = 0xff9300
        self.db_conn = AsyncIOMotorClient(
            secrets_mongo_uri,
            io_loop=bot.loop
        )[secrets_mongo_dbname]
        self.logging = self.db_conn["Logging"]


def setup(bot):
    bot.add_cog(mongoCog(bot))
