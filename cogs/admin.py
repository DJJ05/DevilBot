import discord
from discord.ext import commands

from .utils import checks

class adminCog(commands.Cog):
    """Developer commands"""

    def __init__(self, bot):
        self.bot = bot
        self.db_conn = bot.db_conn
        self.colour = 0xff9300
        self.footer = 'Bot developed by DevilJamJar#0001\nWith a lot of help from ♿nizcomix#7532'
        self.thumb = 'https://styles.redditmedia.com/t5_3el0q/styles/communityIcon_iag4ayvh1eq41.jpg'

    @commands.command(aliases=['devclean', 'botpurge'])
    @checks.check_admin_or_owner()
    async def dev_clean(self, ctx, limit: int = 50):
        """
        Cleans up the bots messages.
        """

        prefix = ctx.prefix

        async with ctx.typing():

            if ctx.channel.permissions_for(ctx.me).manage_messages:
                messages = await ctx.channel.purge(check=lambda m: m.author == ctx.me or m.content.startswith(prefix),
                                                bulk=True, limit=limit)
            else:
                messages = await ctx.channel.purge(check=lambda m: m.author == ctx.me, bulk=False, limit=limit)

            return await ctx.send(f'I found and deleted `{len(messages)}` of my '
                                f'message(s) out of the last `{limit}` message(s).', delete_after=3)

    @commands.command()
    @checks.check_admin_or_owner()
    async def leaveguild(self, ctx):
        """Leaves the guild that the command was executed in."""
        embed=discord.Embed(title='Goodbye! Click here if you would like to reinvite me.', url='https://discord.com/api/oauth2/authorize?client_id=720229743974285312&permissions=2113924179&scope=bot', colour=self.colour)
        await ctx.send(embed=embed)
        await self.bot.get_guild(ctx.guild.id).leave()

def setup(bot):
    bot.add_cog(adminCog(bot))
