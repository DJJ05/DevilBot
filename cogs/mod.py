import asyncio
import json

import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType

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
    @commands.has_permissions(manage_channels=True)
    @commands.max_concurrency(1, BucketType.channel)
    async def lockdown(self, ctx, minutes: float = 30):
        """Locks down all channels in the guild and makes them untalkable"""
        seconds = minutes * 60
        overwrites = {
            ctx.guild.default_role: discord.PermissionOverwrite(
                send_messages=False
            )
        }
        await ctx.send(f"Are you sure you want to lock down this guild for {minutes}m? Type 'yes' or 'no'.")

        def check(m):
            return m.channel.id == ctx.channel.id and m.author.id == ctx.author.id

        try:
            msg = await self.bot.wait_for('message', check=check, timeout=60)
        except asyncio.TimeoutError:
            await ctx.send("You took too long to respond, try again.")
        else:
            if msg.content.lower() in ['yes', 'y', ]:
                channels = []

                for channel in ctx.guild.text_channels:
                    if channel.overwrites_for(ctx.guild.default_role).read_messages != False:
                        if channel.overwrites_for(ctx.guild.default_role).send_messages != False:
                            await channel.edit(overwrites=overwrites)
                            channels.append(channel)

                await ctx.send(f'Alright, I removed everyone\'s perms for the next {minutes}m.')
                await asyncio.sleep(seconds)
                overwrites_revert = {
                    ctx.guild.default_role: discord.PermissionOverwrite(
                        send_messages=True
                    )
                }
                for channel in channels:
                    await channel.edit(overwrites=overwrites_revert)
                return await ctx.reply(f'{ctx.author.mention}, this guild is no longer in lockdown.')
            elif msg.content.lower() in ['no', 'n']:
                return await ctx.reply('Alright, lockdown sequence cancelled.')
            else:
                return await ctx.reply('That\'s not a valid option, try again.')

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason = 'None Provided'):
        """Bans a member from the server"""
        reason = f'Actioned by {ctx.author}: {reason}'
        await ctx.guild.ban(member, reason=reason)
        await ctx.reply(f'Successfully banned {member}.')

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason = 'None Provided'):
        """Kicks a member from the server."""
        reason = f'Actioned by {ctx.author}: {reason}'
        await ctx.guild.kick(member, reason=reason)
        await ctx.reply(f'Successfully kicked {member}')

    @commands.command(aliases=['ud'])
    @commands.has_permissions(manage_messages=True)
    async def snipe(self, ctx):
        """Returns last deleted message in this channel"""
        with open('deleted.json', 'r') as f:
            deleted = json.load(f)
        try:
            a = deleted[str(ctx.channel.id)]
        except:
            raise commands.BadArgument('This channel has no stored deletions!')
        embed = discord.Embed(
            title=f'Last deleted message in #{ctx.channel.name}',
            colour=self.colour,
            description=f'**Author:**\n{deleted[str(ctx.channel.id)]["author"]}\n**Message:**\n{deleted[str(ctx.channel.id)]["message"]}\n**Created At:**\n{deleted[str(ctx.channel.id)]["created"]}'
        )
        embed.set_author(
            name=f'Requested by {ctx.author}', icon_url=ctx.message.author.avatar_url)
        await ctx.reply(embed=embed)

    @commands.command(aliases=['devclean', 'botpurge'])
    @checks.check_mod_or_owner()
    async def dev_clean(self, ctx, limit: int = 50):
        """Cleans up bot messages and invocation contexts"""

        prefix = ctx.prefix if ctx.prefix != '' else 'ow!'

        async with ctx.typing():

            if ctx.channel.permissions_for(ctx.me).manage_messages:
                messages = await ctx.channel.purge(check=lambda m: m.author == ctx.me or m.content.startswith(prefix),
                                                   bulk=True, limit=limit)
            else:
                messages = await ctx.channel.purge(check=lambda m: m.author == ctx.me, bulk=False, limit=limit)

            return await ctx.reply(f'I found and deleted `{len(messages)}` of my '
                                  f'message(s) out of the last `{limit}` message(s).', delete_after=3)


def setup(bot):
    bot.add_cog(modCog(bot))
