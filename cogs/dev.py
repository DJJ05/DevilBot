import asyncio
import json
import os
import textwrap
import traceback

import discord
from discord.ext import commands


class devCog(commands.Cog):
    """Developer commands"""

    def __init__(self, bot):
        self.bot = bot

        self.footer = 'Bot developed by DevilJamJar#0001\nWith a lot of help from ♿nizcomix#7532'
        self.thumb = 'https://styles.redditmedia.com/t5_3el0q/styles/communityIcon_iag4ayvh1eq41.jpg'

    # async def cog_check(self, ctx):
    # return ctx.author.id == 670564722218762240 # check for all commands in this cog

    @commands.command(aliases=['invgrab', 'makeinv'])
    @commands.is_owner()
    async def grabinv(self, ctx, guild: int = None):
        guild = self.bot.get_guild(guild) if guild else ctx.guild
        gchannel = None
        for channel in guild.text_channels:
            if ctx.me.permissions_in(channel).create_instant_invite:
                gchannel = channel
                break
        if not gchannel:
            raise commands.BotMissingPermissions
        invite = await gchannel.create_invite(reason='Invite for logging and testing purposes. Expires in 1 hour.',
                                              max_age=3600)
        await ctx.send('👍')
        dicted = {}
        for i in dir(invite):
            if not str(i).startswith('__') and not str(getattr(invite, i)).startswith('<'):
                dicted[i] = str(getattr(invite, i))
        dicted = json.dumps(dicted, indent=4)
        dicted = str(dicted)
        embed = discord.Embed(
            title=f'Successfully generated invite for {guild.name}',
            description=f'```json\n{dicted}\n```',
            colour=self.bot.colour
        )
        embed.set_thumbnail(url=guild.icon_url)
        await ctx.author.send(embed=embed)
        sent = await ctx.author.send('Say "del" or "delete" to delete this invite link')

        def check(m):
            return m.author.id == ctx.author.id and type(m.channel) == discord.DMChannel and m.content.lower() in [
                'del', 'delete']

        try:
            await self.bot.wait_for('message', check=check, timeout=3600)
        except asyncio.TimeoutError:
            pass
        else:
            await sent.delete()
            await invite.delete()
            await ctx.author.send('Done!')

    @commands.group(invoke_without_command=True, aliases=['bl'])
    @commands.is_owner()
    async def blacklist(self, ctx):
        """Blacklisting commands"""
        pass

    @blacklist.command(aliases=['addmember'])
    @commands.is_owner()
    async def adduser(self, ctx, member: discord.Member, *, reason: str = 'None Provided'):
        with open('blacklist.json', 'r') as f:
            blacklist = json.load(f)

        blacklist['users'][str(member.id)] = reason.capitalize()
        self.bot.blacklist['users'][str(member.id)] = reason.capitalize()

        with open('blacklist.json', 'w') as f:
            json.dump(blacklist, f, indent=4)

        await ctx.send('Done.')

        try:
            embed = discord.Embed(title=f'You have been blacklisted from utilising my commands.',
                                  colour=self.bot.colour,
                                  description=f'Reason: `{reason.capitalize()}`')
            await member.send(embed=embed)
            await ctx.send('DM sent successfully.')
        except:
            await ctx.send('DM failed to send.')

    @blacklist.command(aliases=['remmember'])
    @commands.is_owner()
    async def remuser(self, ctx, member: discord.Member):
        with open('blacklist.json', 'r') as f:
            blacklist = json.load(f)

        try:
            self.bot.blacklist['users'].pop(str(member.id))
            blacklist['users'].pop(str(member.id))
        except:
            return await ctx.send('`Member` not found in blacklist.')

        with open('blacklist.json', 'w') as f:
            json.dump(blacklist, f, indent=4)

        await ctx.send('Done.')

        try:
            embed = discord.Embed(
                title=f'You have been unblacklisted from utilising my commands.', colour=self.bot.colour)
            await member.send(embed=embed)
            await ctx.send('DM sent successfully.')
        except:
            await ctx.send('DM failed to send.')

    @commands.command(name='eval')
    @commands.is_owner()
    async def _eval(self, ctx, *, code):
        if "import os" in code or "import sys" in code:
            return await ctx.send(f"You Can't Do That!")

        code = code.strip('` ')

        env = {
            'bot': self.bot,
            'BOT': self.bot,
            'client': self.bot,
            'ctx': ctx,
            'message': ctx.message,
            'server': ctx.message.guild,
            'guild': ctx.message.guild,
            'channel': ctx.message.channel,
            'author': ctx.message.author,
            'print': ctx.send  # ah yes, await print()
        }
        env.update(globals())

        new_forced_async_code = f'async def code():\n{textwrap.indent(code, "    ")}'

        exec(new_forced_async_code, env)
        code = env['code']
        try:
            await code()
        except:
            await ctx.send(f'```{traceback.format_exc()}```')

    @commands.command(aliases=['tm'])
    @commands.is_owner()
    async def togglemaintenance(self, ctx):
        """Toggles bot maintenance mode"""
        for c in self.bot.walk_commands():
            if c.name != 'togglemaintenance':
                if not c.enabled:
                    c.enabled = True
                else:
                    c.enabled = False
        print('Maintenance has been toggled.')
        return await ctx.send('Successfully `toggled` maintenance mode.')

    @commands.command()
    @commands.is_owner()
    async def load(self, ctx, extension: str = None):
        """Loads a cog."""
        if extension:
            self.bot.load_extension(f'cogs.{extension}')
            return await ctx.send(f'Successfully loaded extension `cogs.{extension}.`')

    @commands.command()
    @commands.is_owner()
    async def unload(self, ctx, extension: str = None):
        """Unloads a cog."""
        if extension:
            self.bot.unload_extension(f'cogs.{extension}')
            return await ctx.send(f'Successfully unloaded extension `cogs.{extension}.`')

    @commands.command()
    @commands.is_owner()
    async def reload(self, ctx, extension: str = None):
        """Reloads all cogs or a specified cog"""
        if not extension:
            for filename in os.listdir('./cogs'):
                if filename.endswith('.py') and filename != 'dev.py' and filename != 'secrets.py':
                    self.bot.unload_extension(f'cogs.{filename[:-3]}')
                    self.bot.load_extension(f'cogs.{filename[:-3]}')
            return await ctx.send('Successfully reloaded extension `all cogs.`')
        self.bot.unload_extension(f'cogs.{extension}')
        self.bot.load_extension(f'cogs.{extension}')
        return await ctx.send(f'Successfully reloaded extension `cogs.{extension}.`')


def setup(bot):
    bot.add_cog(devCog(bot))
