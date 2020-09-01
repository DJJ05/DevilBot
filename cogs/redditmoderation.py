import discord
from discord.ext import commands

import praw, prawcore

from .utils import checks

class redditModerationCog(commands.Cog):
    """r/Overwatch_Memes Moderation related Commands"""

    def __init__(self, bot):
        self.bot = bot
        self.db_conn = bot.db_conn
        self.colour = 0xff9300
        self.footer = 'Bot developed by DevilJamJar#0001\nWith a lot of help from ♿nizcomix#7532'
        self.thumb = 'https://styles.redditmedia.com/t5_3el0q/styles/communityIcon_iag4ayvh1eq41.jpg'

    @commands.command(pass_context=True, aliases=['lb'], invoke_without_command=True)
    @checks.check_mod_server()
    async def leaderboard(self, ctx, amount: int = 10):
        """Displays moderation leaderboard"""
        if 0 < amount < 15:
            pass
        else:
            return await ctx.send('The limit needs to be between `1` and `14`')
        async with ctx.typing():
            record = await self.db_conn.fetch(
                'SELECT "Mod_Name", ("Flair_Removals" * 5 + "Regular_Removals") AS Removals FROM "ModStats" ORDER BY Removals DESC LIMIT $1',
                amount)
            embed = discord.Embed(title=f'Monthly Top {amount} Moderator Actions Leaderboard', color=0xff9300)
            for row in record:
                embed.add_field(
                name=row[0],
                value=row[1],
                inline=False
            )

        embed.set_thumbnail(url=self.thumb)
        embed.set_footer(text=self.footer)
        await ctx.send(embed=embed)

    @commands.command(aliases=['stat', 'overview'])
    @checks.check_mod_server()
    async def stats(self, ctx, *, user:str=None):
        """Displays mod stats for a user, or for you."""
        if not user:
            user = ctx.author.display_name
        user = user.lower()
        async with ctx.typing():
            record = await self.db_conn.fetch(
                'SELECT * FROM "ModStats" WHERE "Mod_Name" = $1', user)
        if not len(record):
            return await ctx.send('Specified user `not found.` Please note that the default user is your `nickname` if another user is not specified.')
        embed=discord.Embed(title=f'Monthly Moderator Stats for u/{record[0][0]}', color=self.colour)
        embed.add_field(name='Flair removals:', value=f'{record[0][1]}', inline=False)
        embed.add_field(name='Regular removals:', value=f'{record[0][2]}', inline=False)
        embed.add_field(name='Total action count:', value=f'{int(record[0][1]) * 5 + int(record[0][2])}', inline=False)
        return await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(redditModerationCog(bot))
