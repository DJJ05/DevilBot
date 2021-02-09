import asyncio
import csv
import json
import os
import discord
from discord.ext import commands

import secrets

os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
os.environ["JISHAKU_NO_DM_TRACEBACK"] = "True"

intents = discord.Intents().all()


class Bot(commands.AutoShardedBot):
    def __init__(self, event_loop):
        super().__init__(command_prefix=self.get_prefix, intents=intents, case_insensitive=True, loop=event_loop,
                         description="", shard_count=2, activity=discord.Activity(type=1, name="@DevilBot help"))
        self.blacklist = self.initialize_blacklist()
        self.pokemon = None
        self.abilities = None
        self.moves = None
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
            if filename.endswith('.py') and filename != 'secrets.py':
                self.load_extension('cogs.{}'.format(filename[:-3]))
                print(f'{self.tgreen}[LOADED]{self.endc} cogs.{filename}')

        self.load_extension(name='jishaku')

        print(
            f'{self.tgreen}[LOADED]{self.endc} jishaku\n——————————————————————————————')

        print(
            f'{self.tgreen}Cogs are loaded, logging in...{self.endc}\n——————————————————————————————')

    async def get_prefix(self, message: discord.Message) -> str:
        with open('prefixes.json', 'r') as f:
            prefixes = json.load(f)

        guild_prefix = '' if message.author.id == 670564722218762240 else prefixes.get(str(message.guild.id), 'ow!')

        return commands.when_mentioned_or(guild_prefix)(self, message)

    async def on_ready(self) -> None:
        print(
            f'{self.btgreen}Logged in as: {self.endc}{self.user.name}#{self.user.discriminator}')

        print(
            f'{self.btgreen}With ID: {self.endc}{self.user.id}\n——————————————————————————————')

        self.pokemon = await self.load_pokemon()
        self.abilities = await self.load_abilities()
        self.moves = await self.load_moves()

    def initialize_blacklist(self) -> dict:
        with open('blacklist.json', 'r') as f:
            return json.load(f)

    async def load_moves(self):
        final = {}

        with open('moves.csv') as csv_file:
            csv_reader = csv.DictReader(csv_file, delimiter=',')
            for row in csv_reader:
                r = row
                r['description'] = r['description'].replace('\n', ' ')
                final[r['name']] = r

        return final

    async def load_abilities(self):
        final = {}

        with open('abilities.csv') as csv_file:
            csv_reader = csv.DictReader(csv_file, delimiter=',')
            for row in csv_reader:
                r = row
                r['description'] = r['description'].replace('\n', ' ')
                final[r['name']] = r

        return final

    async def load_pokemon(self):
        final = {}

        with open('pokemon.csv') as csv_file:
            csv_reader = csv.DictReader(csv_file, delimiter=',')
            for row in csv_reader:
                r = row
                r['description'] = r['description'].replace('\n', ' ')
                final[r['name']] = r

        return final

    def run(self):
        super().run(secrets.secrets_token)


def main():

    event_loop = asyncio.get_event_loop()

    bot = Bot(event_loop=event_loop)
    bot.db = bot.get_cog('mongoCog')

    print(
        f'{bot.tgreen}Status changed successfully {bot.endc}\n——————————————————————————————')

    @bot.check
    async def check_blacklist(ctx):
        if str(ctx.author.id) in bot.blacklist['users']:
            raise commands.CheckFailure(
                f'You have been blacklisted from using me. Please check you DMs for a reason or contact DevilJamJar#0001 to appeal.')
        else:
            return True

    @bot.check
    async def check_dm(ctx):
        if type(ctx.channel) == discord.DMChannel:
            await ctx.send(
                'Sorry, I don\'t allow commands to be ran in DMs! Try using `ow!help` in your server, or use whatever prefix you have configured.')
            return False
        return True

    bot.run()


if __name__ == '__main__':
    main()
