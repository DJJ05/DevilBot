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
        try:
            record = await self.db_conn.fetch(
                'SELECT "Mod_Name", ("Flair_Removals" * 5 + "Regular_Removals") AS Removals FROM "ModStatsAug" ORDER BY Removals DESC LIMIT $1',
                amount)
        except Exception as e:
            print(e)
            return await ctx.send(f'Failed to get a valid connection and execution of the database')

        embed = discord.Embed(title=f'Monthly Top {amount} Moderator Actions Leaderboard', color=0xff9300)
        embed.set_thumbnail(url=self.thumb)

        mods = []
        actions = []
        i = [f"{index}) {value}" for index, value in enumerate(mods, 1)]
        for row in record:
            mods.append(row[0])
            actions.append(row[1])

        for mod, action in zip(i, actions):
            embed.add_field(name=mod, value=action, inline=False)

        embed.set_footer(text=self.footer)

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(redditModerationCog(bot))
