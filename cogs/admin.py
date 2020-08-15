import discord
from discord.ext import commands
import json

from .utils import checks

class adminCog(commands.Cog):
    """Admin commands"""

    def __init__(self, bot):
        self.bot = bot
        self.db_conn = bot.db_conn
        self.colour = 0xff9300
        self.footer = 'Bot developed by DevilJamJar#0001\nWith a lot of help from ♿nizcomix#7532'
        self.thumb = 'https://styles.redditmedia.com/t5_3el0q/styles/communityIcon_iag4ayvh1eq41.jpg'

    @commands.command()
    @checks.check_admin_or_owner()
    async def leaveguild(self, ctx):
        """Leaves the guild that the command was executed in."""
        embed=discord.Embed(title='Goodbye! Click here if you would like to reinvite me.', url='https://discord.com/api/oauth2/authorize?client_id=720229743974285312&permissions=2113924179&scope=bot', colour=self.colour)
        await ctx.send(embed=embed)
        await self.bot.get_guild(ctx.guild.id).leave()

    @commands.command(aliases=["pre", "prefix", "changpre", "prechange", "prefixchange"])
    @checks.check_admin_or_owner()
    async def changeprefix(self, ctx, prefix:str='ow!'):
        """Changes the guild prefix"""
        if prefix == 'ow!':
            with open ('prefixes.json', 'r') as f:
                prefixes = json.load(f)
            prefixes[str(ctx.guild.id)] = prefix
            with open ('prefixes.json', 'w') as f:
                json.dump(prefixes, f, indent=4)
            await ctx.send(f'Successfully `reset` guild prefix to `{prefix}`')
            await ctx.guild.me.edit(nick=f'[{prefix}] DevilBot')
        else:
            with open ('prefixes.json', 'r') as f:
                prefixes = json.load(f)
            prefixes[str(ctx.guild.id)] = prefix
            with open ('prefixes.json', 'w') as f:
                json.dump(prefixes, f, indent=4)
            await ctx.send(f'Successfully `changed` guild prefix to {prefix}')
            await ctx.guild.me.edit(nick=f'[{prefix}] DevilBot')

def setup(bot):
    bot.add_cog(adminCog(bot))
