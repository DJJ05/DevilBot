import discord
from discord.ext import commands

class devCog(commands.Cog):
    """Developer commands"""

    def __init__(self, bot):
        self.bot = bot
        self.db_conn = bot.db_conn
        self.colour = 0xff9300
        self.footer = 'Bot developed by DevilJamJar#0001\nWith a lot of help from ♿nizcomix#7532'
        self.thumb = 'https://styles.redditmedia.com/t5_3el0q/styles/communityIcon_iag4ayvh1eq41.jpg'

    @commands.command(aliases=['tm'])
    async def ToggleMaintenance(self, ctx):
        """Toggles bot maintenance mode"""
        for c in self.bot.commands:
            if c.name != 'ToggleMaintenance':
                if c.enabled == False:
                    c.enabled = True
                else:
                    c.enabled = False
        return await ctx.send('Successfully `toggled` maintenance mode.')

def setup(bot):
    bot.add_cog(devCog(bot))
