# -*- coding: utf-8 -*-

from discord.ext import commands


class events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        await self.bot.process_commands(after)


def setup(bot):
    bot.add_cog(events(bot))
