# -*- coding: utf-8 -*-

import time

import discord
from discord.ext import commands


class DevilBotHelp(commands.MinimalHelpCommand):
    async def send_pages(self):
        destination = self.get_destination()
        for page in self.paginator.pages:
            emby = discord.Embed(description=page, colour=0x860111)
            await destination.send(embed=emby)


class meta(commands.Cog):
    """Meta cog"""

    def __init__(self, bot):
        self.bot = bot
        self._original_help_command = bot.help_command
        bot.help_command = DevilBotHelp()
        bot.help_command.cog = self

    def cog_unload(self):
        self.bot.help_command = self._original_help_command

    @commands.command(aliases=['git', 'github'])
    async def source(self, ctx, command_name=None):
        """Returns specific command source code"""
        if not command_name:
            await ctx.reply('https://github.com/DevilJamJar/DevilBot')
        jsk = self.bot.get_command('jishaku source')
        await ctx.invoke(jsk, command_name=command_name)

    @commands.command(aliases=['latency'])
    async def ping(self, ctx):
        """Returns bot latency and response time"""
        latency = f'{round(self.bot.latency * 1000)}ms'
        start = time.perf_counter()
        pong = await ctx.reply(f'API Latency: {latency}')
        end = time.perf_counter()
        response = f'{round((end - start) * 1000)}ms'
        await pong.edit(content=f'API Latency: {latency}\nResponse Time: {response}')

    @commands.command(aliases=['inv'])
    async def invite(self, ctx):
        """Returns bot invite URL"""
        await ctx.reply(
            'https://discord.com/api/oauth2/authorize?client_id=720229743974285312&permissions=67464257&scope=bot')


def setup(bot):
    bot.add_cog(meta(bot))
