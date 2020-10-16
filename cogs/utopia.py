import discord
from discord.ext import commands
import json, random, typing
from discord.ext.commands.cooldowns import BucketType
from .utils.checks import check_admin_or_owner

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

    @commands.group(invoke_without_command=True, aliases=['reputation'])
    async def rep(self, ctx, *, member:typing.Union[discord.Member, int]=None):
        if not member:
            member = ctx.author
        elif type(member) == int:
            try:
                member = self.bot.get_user(member) or await self.bot.fetch_user(member)
            except:
                raise commands.BadArgument('Member not found')
        with open('rep.json', 'r') as f:
            data = json.load(f)
        try:
            a = data[str(member.id)]
        except KeyError:
            send = f'{member} has `0` reputation.'
        else:
            send = f'{member} has `{data[str(member.id)]["reputation"]}` reputation.'
            for i in data[str(member.id)]:
                if i != 'reputation':
                    send+=(f'\n`{data[str(member.id)].get(i)}`')
        return await ctx.send(send)

    @rep.command(aliases=['remove'])
    @check_admin_or_owner()
    async def take(self, ctx, *, reason):
        """Takes reason as the words provided as the reason, use rep <user> to see the reasons"""
        with open('rep.json', 'r') as f:
            data = json.load(f)
        success = []
        for i in data:
            pass

    @rep.command(aliases=['lb'])
    async def leaderboard(self, ctx):
        """Reputation leaderboard"""
        with open('rep.json', 'r') as f:
            data = json.load(f)
        send=f'__**Reputation Leaderboard. Use {ctx.prefix}rep <user> to view their rep breakdown.**__'
        dsorted = sorted(data.keys(), key=lambda x: (data[x]['reputation']), reverse=True)
        number = 1
        for i in dsorted:
            member = self.bot.get_user(int(i)) or await self.bot.fetch_user(int(i))
            send+=f'\n{number}) {member} – `{data[i]["reputation"]}`'
            number += 1
        await ctx.send(send)

    @rep.command(aliases=['add'])
    @commands.cooldown(1,120,BucketType.user) 
    async def give(self, ctx, member:typing.Union[discord.Member, int], *, reason):
        """Give reputation"""
        if type(member) == int:
            try:
                member = self.bot.get_user(member) or await self.bot.fetch_user(member)
            except:
                raise commands.BadArgument('Member not found')
        if member == ctx.author:
            raise commands.BadArgument('Woooooooooow, yeah I\'m not gonna do that bud.')
        with open('rep.json', 'r') as f:
            data = json.load(f)
        try:
            data[str(member.id)]['reputation'] += 1
        except KeyError:
            data[str(member.id)] = {"reputation":1}
        data[str(member.id)][ctx.message.jump_url] = f'– {reason}'
        with open('rep.json', 'w') as f:
            json.dump(data, f, indent=4)
        await ctx.send(f'Awarded {member} `1` reputation. View their reputation overview with `{ctx.prefix}rep {member.id}`.')

    @commands.command()
    async def nominate(self, ctx, message:discord.Message):
        """Nominate a message"""
        with open('nominees.json', 'r') as f:
            nominees = json.load(f)
        finmsg=message.clean_content
        if len(message.attachments):
            for i in message.attachments:
                finmsg+=f'\n{i.url}'
        nominees[f'{str(finmsg)}∫√∆{str(message.author)}∫√∆{str(message.created_at)}'] = str(message.id)
        with open('nominees.json', 'w') as f:
            json.dump(nominees, f, indent=4)
        channel = self.bot.get_channel(752472138299998238)
        embed=discord.Embed(
            colour = self.colour,
            description=f'**Message:**\n{str(finmsg)}\n**Author:**\n{str(message.author)}\n**Created At:**\n{str(message.created_at)}\n**Jump:**\n{str(message.jump_url)}'
        )
        await channel.send(embed=embed)
        await ctx.send(f'{ctx.author.mention}, successfully inserted message into nominations. Use {ctx.prefix}utopiaquote for a random one!')

    @commands.command(aliases=['uq', 'utopiaq', 'uquote'])
    async def utopiaquote(self, ctx):
        """Get a random quote from utopia"""
        full=[]
        with open('nominees.json', 'r') as f:
            nominees = json.load(f)
        for i in nominees:
            full.append(i)
        final = random.choice(full)
        final = final.split('∫√∆')
        embed=discord.Embed(
            colour = self.colour,
            description=f'**Message:**\n{final[0]}\n**Author:**\n{final[1]}\n**Created At:**\n{final[2]}'
        )
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(utopiaCog(bot))