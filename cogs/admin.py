import json

from discord.ext import commands

from .utils import checks


class adminCog(commands.Cog):
    """Admin commands"""

    def __init__(self, bot):
        self.bot = bot

        self.footer = 'Bot developed by DevilJamJar#0001\nWith a lot of help from ♿nizcomix#7532'
        self.thumb = 'https://styles.redditmedia.com/t5_3el0q/styles/communityIcon_iag4ayvh1eq41.jpg'

    @commands.command(aliases=["pre", "prefix", "changpre", "prechange", "prefixchange"])
    @checks.check_admin_or_owner()
    async def changeprefix(self, ctx, prefix: str = 'ow!'):
        """Changes the guild prefix"""
        if prefix == 'ow!':
            with open('prefixes.json', 'r') as f:
                prefixes = json.load(f)
            prefixes[str(ctx.guild.id)] = prefix
            with open('prefixes.json', 'w') as f:
                json.dump(prefixes, f, indent=4)
            await ctx.send(f'Successfully `reset` guild prefix to `{prefix}`')
            await ctx.guild.me.edit(nick=f'[{prefix}] DevilBot')
        else:
            with open('prefixes.json', 'r') as f:
                prefixes = json.load(f)
            prefixes[str(ctx.guild.id)] = prefix
            with open('prefixes.json', 'w') as f:
                json.dump(prefixes, f, indent=4)
            await ctx.send(f'Successfully `changed` guild prefix to {prefix}')
            await ctx.guild.me.edit(nick=f'[{prefix}] DevilBot')


def setup(bot):
    bot.add_cog(adminCog(bot))
