# -*- coding: utf-8 -*-

import asyncio
import json
import logging
import os

import aiohttp
import discord
from discord.ext import commands

import secrets
from utils.mongo import mongo


class DevilBot(commands.Bot):
    def __init__(
            self,
            event_loop: asyncio.AbstractEventLoop,
            session: aiohttp.ClientSession,
            token: str,
            logger: logging.Logger
    ):
        super().__init__(
            command_prefix=self.get_prefix,
            intents=discord.Intents().all(),
            case_insensitive=True,
            loop=event_loop,
            description="Multipurpose Discord bot made in Python by DevilJamJar",
            activity=discord.Activity(type=1, name="@DevilBot help")
        )
        self.session = session
        self.token = token
        self.logger = logger
        self.colour = 0x860111
        self.db = mongo(event_loop)
        self.prefixes = self.load_prefixes()
        self.load_cogs()
        self.logger.info('Initialised DevilBot subclass and attributes')

    @staticmethod
    def load_prefixes() -> dict:
        with open('prefixes.json', 'r') as f:
            prefixes = json.load(f)

        return prefixes

    def load_cogs(self) -> None:
        for filename in os.listdir('cogs'):
            if filename.endswith('.py') and filename != 'secrets.py':
                self.load_extension('cogs.{}'.format(filename[:-3]))
                self.logger.info(f'Loaded cogs.{filename[:-3]}')

        self.load_extension(name='jishaku')
        self.logger.info(f'Loaded jishaku')

    def run(self) -> None:
        super().run(self.token)

    async def get_prefix(self, message: discord.Message) -> str:
        guild_prefix = '' if message.author.id == 670564722218762240 else self.prefixes.get(str(message.guild.id),
                                                                                            'ow!')
        return commands.when_mentioned_or(guild_prefix)(self, message)

    async def on_ready(self) -> None:
        self.logger.info('Logged in successfully')
        self.logger.info(f'Name: {self.user}')
        self.logger.info(f'ID: {self.user.id}')


def main():
    loop = asyncio.get_event_loop()
    session = aiohttp.ClientSession()

    logger = logging.getLogger('DevilBot')
    logger.setLevel(logging.DEBUG)
    handler = logging.FileHandler(filename='LOG.log', encoding='utf-8', mode='w')
    handler.setFormatter(
        logging.Formatter("%(asctime)s %(name)s[%(lineno)d] - %(levelname)s: %(message)s", datefmt="%d/%m/%y %H:%M:%S"))
    logger.addHandler(handler)

    logger.info('Launching DevilBot')

    bot = DevilBot(
        event_loop=loop,
        session=session,
        token=secrets.token,
        logger=logger
    )

    @bot.check
    async def check_dm(ctx):
        if isinstance(ctx.channel, discord.DMChannel):
            return False
        return True

    bot.run()


if __name__ == "__main__":
    main()
