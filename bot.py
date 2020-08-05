import asyncio

from discord.ext import commands
import discord
import sys
import json, os
import secrets
import asyncpg

class Bot(commands.Bot):
    def __init__(self, database_conn, event_loop):
        super().__init__(command_prefix=self.get_prefix, case_insensitive=True, loop=event_loop,
                         description="Bot developed by DevilJamJar#0001\nWith a lot of help from ♿nizcomix#7532")
        self.db_conn = database_conn
        self.colour = 0xff9300
        self.footer = 'Bot developed by DevilJamJar#0001\nWith a lot of help from ♿nizcomix#7532'
        self.thumb = 'https://styles.redditmedia.com/t5_3el0q/styles/communityIcon_iag4ayvh1eq41.jpg'

        for filename in os.listdir('cogs'):
            if filename.endswith('.py') and filename != 'secrets.py':
                self.load_extension('cogs.{}'.format(filename[:-3]))
        self.load_extension(name='jishaku')
        print('Cogs are loaded...')

    async def get_prefix(self, message: discord.Message) -> str:
        with open('prefixes.json', 'r') as f:
            prefixes = json.load(f)

        return prefixes[str(message.guild.id)]

    async def on_ready(self) -> None:
        print('We have logged in!')
        await self.change_presence(
            activity=discord.Activity(type=discord.ActivityType.watching, name="http://overwatchmemesbot.ezyro.com"))

    def run(self):
        super().run(secrets.secrets_token)

class DataBase:
    db_conn = None

    @staticmethod
    async def initiate_database() -> bool:
        try:
            DataBase.db_conn = await asyncpg.create_pool(user=secrets.secrets_pg_user,
                                                         password=secrets.secrets_pg_password,
                                                         host=secrets.secrets_pg_host,
                                                         port=secrets.secrets_pg_port,
                                                         database=secrets.secrets_pg_database,
                                                         )
            return True

        except Exception as err:
            print('Failed to connect to database', err)
            raise

def main():
    
    if not DataBase.initiate_database():
        sys.exit()

    event_loop = asyncio.get_event_loop()
    if not event_loop.run_until_complete(DataBase.initiate_database()):
        sys.exit()

    bot = Bot(database_conn=DataBase.db_conn, event_loop=event_loop)
    # bot.remove_command('help')
    bot.run()

if __name__ == '__main__':
    main()
