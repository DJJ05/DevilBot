from discord.ext import commands
import discord
import json, os
from secrets import secrets_token

class DevilBot(commands.AutoShardedBot):
    def __init__(self):
        super().__init__(command_prefix=self.get_prefix, pm_help=None, case_insensitive=True)

        self.colour = 0xff9300
        self.footer = 'Bot developed by DevilJamJar#0001\nWith a lot of help from ♿nizcomix#7532'
        self.thumb = 'https://styles.redditmedia.com/t5_3el0q/styles/communityIcon_iag4ayvh1eq41.jpg'

    async def get_prefix(self, message):
        with open ('prefixes.json', 'r') as f:
            prefixes = json.load(f)

        return prefixes[str(message.guild.id)]

    async def on_guild_join(self, guild):
        with open ('prefixes.json', 'r') as f:
            prefixes = json.load(f)

        prefixes[str(guild.id)] = 'ow!'

        with open ('prefixes.json', 'w') as f:
            json.dump(prefixes, f, indent=4)

        a = sorted([c for c in guild.text_channels if c.permissions_for(guild.me).send_messages], key=lambda x: x.position)
        channel =  a[0]
        inv = await channel.create_invite()
        finalinv = f"https://discord.gg/{inv.code}"

        c = self.get_channel(715744000077725769)

        embed = discord.Embed(colour=0xff9300, title=f'{guild}',
                            description=f"**{guild.id}**\n**{finalinv}**")
        embed.set_thumbnail(url=guild.icon_url)
        await c.send(f"<@!670564722218762240> We joined guild **#{len(self.guilds)}**", embed=embed)

    async def on_guild_remove(self, guild):
        with open ('prefixes.json', 'r') as f:
            prefixes = json.load(f)

        prefixes.pop(str(guild.id))

        with open ('prefixes.json', 'w') as f:
            json.dump(prefixes, f, indent=4)

    async def on_ready(self):
        for filename in os.listdir('cogs'):
            if filename.endswith('.py') and filename != 'secrets.py':
                self.load_extension('cogs.{}'.format(filename[:-3]))
        self.load_extension(name='jishaku')
        print ('Bot is online and cogs do be loaded')
        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="http://overwatchmemesbot.ezyro.com"))

client = DevilBot()
client.remove_command('help')
client.run(secrets_token)