import asyncio

from discord.ext import commands
import discord
import sys
import json, os
import secrets
import asyncpg

os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
os.environ["JISHAKU_NO_DM_TRACEBACK"] = "True" 

intents = discord.Intents().all()

class Bot(commands.AutoShardedBot):
    def __init__(self):
        super().__init__(command_prefix=self.get_prefix, intents=intents, case_insensitive=True,
                         description="")
        self.db_conn = self.loop.run_until_complete(self.init_db())
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

        print('——————————————————————————————')
        for filename in os.listdir('cogs'):
            if filename.endswith('.py') and filename not in ('secrets.py', 'dagpi.py'):
                self.load_extension('cogs.{}'.format(filename[:-3]))
                print(f'{self.tgreen}[LOADED]{self.endc} cogs.{filename}')
        self.load_extension(name='jishaku')
        print(f'{self.tgreen}[LOADED]{self.endc} jishaku\n——————————————————————————————')
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
            activity=discord.Activity(type=5, name="ow!help"))
        print(f'{self.tgreen}Status changed successfully {self.endc}\n——————————————————————————————')
        
    async def init_db(self):
        return await asyncpg.create_pool(user=secrets.secrets_pg_user,
                                                         password=secrets.secrets_pg_password,
                                                         host=secrets.secrets_pg_host,
                                                         port=secrets.secrets_pg_port,
                                                         database=secrets.secrets_pg_database,
                                                         )
        
    def initialize_blacklist(self) -> dict:
        with open('blacklist.json', 'r') as f:
            return json.load(f)

    def run(self):
        super().run(secrets.secrets_token)


bot = Bot()

@bot.check
async def check_blacklist(ctx):
    if str(ctx.author.id) in bot.blacklist['users']:
        raise commands.CheckFailure(f'You have been blacklisted from using me. Please check you DMs for a reason or contact DevilJamJar#0001 to appeal.')
    else:
        return True
    
bot.run()
