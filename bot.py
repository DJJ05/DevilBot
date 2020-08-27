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
        self.blacklist = self.initialize_blacklist()
        self.colour = 0xff9300
        self.footer = 'Bot developed by DevilJamJar#0001\nWith a lot of help from ♿nizcomix#7532'
        self.thumb = 'https://styles.redditmedia.com/t5_3el0q/styles/communityIcon_iag4ayvh1eq41.jpg'

        self.btgreen = '\033[1;32m'
        self.tgreen = '\033[32m'
        self.btmag = '\033[1;35m'
        self.tmag = '\033[35m'
        self.btred = '\033[1;31m'
        self.tred = '\033[31m'
        self.endc = '\033[m'

        for filename in os.listdir('cogs'):
            if filename.endswith('.py') and filename != 'secrets.py':
                self.load_extension('cogs.{}'.format(filename[:-3]))
        self.load_extension(name='jishaku')
        print(self.btmag + r'''
██████╗ ███████╗██╗   ██╗██╗██╗     ██████╗  ██████╗ ████████╗
██╔══██╗██╔════╝██║   ██║██║██║     ██╔══██╗██╔═══██╗╚══██╔══╝
██║  ██║█████╗  ██║   ██║██║██║     ██████╔╝██║   ██║   ██║   
██║  ██║██╔══╝  ╚██╗ ██╔╝██║██║     ██╔══██╗██║   ██║   ██║   
██████╔╝███████╗ ╚████╔╝ ██║███████╗██████╔╝╚██████╔╝   ██║   
╚═════╝ ╚══════╝  ╚═══╝  ╚═╝╚══════╝╚═════╝  ╚═════╝    ╚═╝   
        ''' + self.endc)
        print(f'{self.tgreen}Cogs are loaded, logging in...{self.endc}\n——————————————————————————————')

    async def get_prefix(self, message: discord.Message) -> str:
        with open('prefixes.json', 'r') as f:
            prefixes = json.load(f)
        guild_prefix = prefixes.get(str(message.guild.id), "ow!")		
        return commands.when_mentioned_or(guild_prefix)(self, message)

    async def on_ready(self) -> None:
        print(f'{self.btgreen}Logged in as: {self.endc}{self.user.name}#{self.user.discriminator}')
        print(f'{self.btgreen}With ID: {self.endc}{self.user.id}\n——————————————————————————————')
        await self.change_presence(
            activity=discord.Activity(type=discord.ActivityType.watching, name="the Umbrella Academy"))
        print(f'{self.tgreen}Status changed successfully {self.endc}\n——————————————————————————————')
        
    def initialize_blacklist(self) -> dict:
        with open('blacklist.json', 'r') as f:
            return json.load(f)

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
            print(f'\033[31m Failed to connect to database \033[1;31m', err, '\033[m \n——————————————————————————————')
            raise

def main():
    
    if not DataBase.initiate_database():
        sys.exit()

    event_loop = asyncio.get_event_loop()
    if not event_loop.run_until_complete(DataBase.initiate_database()):
        sys.exit()

    bot = Bot(database_conn=DataBase.db_conn, event_loop=event_loop)

    @bot.check
    async def check_blacklist(ctx):
        if str(ctx.author.id) in bot.blacklist['users']:
            raise commands.CheckFailure(f'You have been blacklisted from using me. Please check you DMs for a reason or contact DevilJamJar#0001 to appeal.')
        else:
            return True

    # bot.remove_command('help')
    bot.run()

if __name__ == '__main__':
    main()
