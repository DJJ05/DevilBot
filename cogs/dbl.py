import json
import discord
from discord.ext import commands, tasks
import aiohttp

from .secrets import secrets_dbl as SECRETS_DBL

BASEURL = 'https://top.gg/api'
CHECKURL = BASEURL + '/bots/720229743974285312/check'
VOTESURL = BASEURL + '/bots/720229743974285312/votes'
UPDATEURL = BASEURL + '/bots/720229743974285312/stats'
HEADERS = {'Authorization': SECRETS_DBL}


async def checkvoter(userid: int) -> bool:
    params = {'userId': userid}
    async with aiohttp.ClientSession() as cs:
        async with cs.get(CHECKURL, headers=HEADERS, params=params) as resp:
            data = await resp.json()
    if bool(data['voted']):
        return True
    return False


async def checkvotes() -> list:
    async with aiohttp.ClientSession() as cs:
        async with cs.get(VOTESURL, headers=HEADERS) as resp:
            data = await resp.json()
    return data


async def updatedbl(bot) -> dict:
    guilds = len(bot.guilds)
    shards = len(bot.shards)
    params = {'server_count': guilds, 'shard_count': shards}
    async with aiohttp.ClientSession() as cs:
        async with cs.post(UPDATEURL, headers=HEADERS, data=params) as resp:
            data = await resp.json()
    return data

VOTELOCKTEMP = discord.Embed(
    colour=0xff9300,
    title='This command is votelocked!',
    description='Apologies, but this command has been **votelocked**. This means that it is only available for people that have voted for **DevilBot on top.gg** to help support its growth! Voting is **quick** and **easy** and helps me out tenfold.\n\n[To use this command please vote](https://bit.ly/vote-devilbot) (it may take up to **10 seconds** to update the bot).'
)
VOTELOCKTEMP.set_thumbnail(
    url='https://cdn.discordapp.com/attachments/745950521072025714/766734683479998574/attention.png')


class dblCog(commands.Cog):
    """Handles interactions with the top.gg API"""

    def __init__(self, bot):
        self.bot = bot
        self.db_conn = bot.db_conn
        self.colour = 0xff9300
        self.update_dbl.start()

    @tasks.loop(minutes=30)
    async def update_dbl(self):
        await updatedbl(self.bot)

    @commands.group(invoke_without_command=True)
    async def vote(self, ctx):
        """top.gg API vote centered commands"""
        voted = await checkvoter(userid=ctx.author.id)
        if voted:
            desc = '**have** voted, and so have access to DevilBot\'s vote-locked commands! Huge thank you!'
        else:
            desc = '**have not** voted, and do not have access to DevilBot\'s vote-locked commands! Voting really helps out my growth and gives you some great perks too!'
        embed = discord.Embed(
            colour=self.colour,
            description=f'Currently you {desc}',
            title='You can vote at __**https://bit.ly/vote-devilbot**__'
        )
        await ctx.send(embed=embed)

    @vote.command()
    @commands.is_owner()
    async def manual_update(self, ctx):
        resp = await updatedbl(self.bot)
        await ctx.send('Success!') if not len(resp.keys()) else await ctx.send(resp)

    @vote.command()
    async def check(self, ctx, user: discord.Member = None):
        if not user:
            user = ctx.author
        voted = await checkvoter(userid=user.id)
        if not voted:
            desc = '**has not** voted :('
        else:
            desc = '**has** voted :D'
        embed = discord.Embed(
            colour=self.colour,
            description=f'{user.mention} {desc}',
            title='Vote Check'
        )
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(dblCog(bot))
