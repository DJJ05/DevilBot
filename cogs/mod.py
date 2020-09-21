import discord
from discord.ext import commands
import json
import typing

from .utils import checks

class modCog(commands.Cog):
    """Mod commands"""

    def __init__(self, bot):
        self.bot = bot
        self.db_conn = bot.db_conn
        self.colour = 0xff9300
        self.footer = 'Bot developed by DevilJamJar#0001\nWith a lot of help from ♿nizcomix#7532'
        self.thumb = 'https://styles.redditmedia.com/t5_3el0q/styles/communityIcon_iag4ayvh1eq41.jpg'

    @commands.command()
    @checks.check_mod_or_owner()
    async def ban(self, ctx, member:typing.Union[discord.Member, int], *, reason:str='None Provided'):
        """Bans a member"""
        if not member:
            return await ctx.send('`Member` is a required argument that is missing.')
        if type(member) == int:
            member = self.bot.get_user(member) or await self.bot.fetch_user(member)
        else:
            if member.top_role > ctx.guild.me.top_role:
                return await ctx.send('I am not permitted to `ban` this member.')
        await ctx.guild.ban(user=member, reason=reason)
        await ctx.send(f'Successfully `banned` {member.mention} from the guild.')
        embed = discord.Embed(title=f'You have been banned from {ctx.guild.name}', colour=self.colour,
                              description=f'By:\n`{ctx.author.name}`\nBecause:\n`{reason}`')
        try:
            await member.send(embed=embed)
        except:
            await ctx.send(f'Attempt to `message` {member.mention} failed.')

    @commands.command(aliases=['yeet'])
    @checks.check_mod_or_owner()
    async def kick(self, ctx, member:discord.Member=None, *, reason:str='None Provided'):
        """Kicks a member"""
        if not member:
            return await ctx.send('`Member` is a required argument that is missing.')
        if member.top_role > ctx.guild.me.top_role:
            return await ctx.send('I am not permitted to `kick` this member.')
        await member.kick(reason=reason)
        await ctx.send(f'Successfully `kicked` {member.mention} from the guild.')
        embed = discord.Embed(title=f'You have been kicked from {ctx.guild.name}', colour=self.colour,
                              description=f'By:\n`{ctx.author.name}`\nBecause:\n`{reason}`')
        try:
            await member.send(embed=embed)
        except:
            await ctx.send(f'Attempt to `message` {member.mention} failed.')

    @commands.command(aliases=['ud'])
    @checks.check_mod_or_owner()
    async def snipe(self, ctx):
        """Returns last deleted message in this channel"""
        with open('deleted.json', 'r') as f:
            deleted = json.load(f)
        embed = discord.Embed(
            title = f'Last deleted message in #{ctx.channel.name}',
            colour = self.colour,
            description = f'**Author:**\n{deleted[str(ctx.channel.id)]["author"]}\n**Message:**\n{deleted[str(ctx.channel.id)]["message"]}\n**Created At:**\n{deleted[str(ctx.channel.id)]["created"]}'
        )
        embed.set_author(name=f'Requested by {ctx.author}', icon_url=ctx.message.author.avatar_url)
        await ctx.send(embed=embed)

    @commands.command(aliases=['devclean', 'botpurge'])
    @checks.check_mod_or_owner()
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

def setup(bot):
    bot.add_cog(modCog(bot))
