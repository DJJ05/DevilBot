import discord
from discord.ext import commands
import json
import random
from datetime import datetime as dt

class utopiaCog(commands.Cog):
    """Utopian-only commands"""

    def __init__(self, bot):
        self.bot = bot
        self.db_conn = bot.db_conn
        self.colour = 0xff9300
        self.footer = 'Bot developed by DevilJamJar#0001\nWith a lot of help from ♿nizcomix#7532'
        self.thumb = 'https://styles.redditmedia.com/t5_3el0q/styles/communityIcon_iag4ayvh1eq41.jpg'

    async def cog_check(self, ctx):
        return ctx.guild.id == 621044091056029696
    
    @property
    def channel(self):
        return self.bot.get_channel(752472138299998238)
    
    async def get_user(self, id: int):
        try:
            user = self.bot.get_user(id) or await self.bot.fetch_user(id)
        except Exception as error:
            raise error
        return user

    @commands.command()
    async def nominate(self, ctx, message:discord.Message):
        with open('nominees.json', 'r') as f:
            nominees = json.load(f)
        finmsg=message.clean_content
        if len(message.attachments):
            for i in message.attachments:
                finmsg+=f'\n{i.url}'
        nominees[str(message.id)] = {'author': message.author.id, 'content': str(finmsg), 'created': str(message.created_at), 'url': message.jump_url}
        with open('nominees.json', 'w') as f:
            json.dump(nominees, f, indent=4)
        embed=discord.Embed(
            colour = self.colour,
            description=f"""
            **Message:**:
            {finmsg}
            **Author:**
            {str(message.author)}
            **Created At:**
            {str(message.created_at)}
            **Jump:**
            {str(message.jump_url)}
            """
        )
        await channel.send(embed=embed)
        await ctx.send(f'{ctx.author.mention}, successfully inserted message into nominations. Use {ctx.prefix}utopiaquote for a random one!')

    @commands.command(aliases=['uq', 'utopiaq', 'uquote'])
    async def utopiaquote(self, ctx):
        full=[]
        with open('nominees.json', 'r') as f:
            nominees = json.load(f)
        choice = random.choice(*[i[1] for i in nominees.items()])
        msg = nominees.get(choice)
        created = dt.strptime(msg['created'], '%Y-%m-%d %H:%M:%S.%f') # an actual datetime object
        embed=discord.Embed(
            colour = self.colour,
            description=f'**Message:**\n{msg['content']}\n**Author:**\n{await self.get_user(msg['author'])}\n**Created At:**\n{created.strftime("%B %d, %Y")}'
        )
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(utopiaCog(bot))
