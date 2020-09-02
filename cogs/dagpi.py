import discord
from discord.ext import commands
import secrets
from asyncdagpi import Client
from asyncdagpi import exceptions

API_CLIENT = Client(secrets.secrets_dagpi_token)

class dagpiCog(commands.Cog):
    """Commands that utilise Daggy's API (dagpi.tk)"""

    def __init__(self, bot):
        self.bot = bot
        self.db_conn = bot.db_conn
        self.colour = 0xff9300
        self.footer = 'Bot developed by DevilJamJar#0001\nWith a lot of help from ♿nizcomix#7532'
        self.thumb = 'https://styles.redditmedia.com/t5_3el0q/styles/communityIcon_iag4ayvh1eq41.jpg'

    @commands.command()
    async def hitler(self, ctx, *, image_url=None):
        try:
            image_url = int(image_url)
            try:
                a = self.bot.get_user(image_url)
                image_url = str(a.avatar_url)
            except:
                raise commands.BadArgument('Unknown User')
        except:
            if not image_url:
                image_url = str(ctx.author.avatar_url)
        try:
            response = await API_CLIENT.staticimage('hitler',image_url)
            await ctx.send(response)
        except Exception as e:
            raise commands.BadArgument(str(e))

def setup(bot):
    bot.add_cog(dagpiCog(bot))
