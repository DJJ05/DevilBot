# -*- coding: utf-8 -*-

import json

from discord.ext import commands


class groveCog(commands.Cog):
    """Grove-only commands"""

    def __init__(self, bot):
        self.bot = bot
        self.db_conn = bot.db_conn
        self.colour = 0xff9300
        self.cooldowns = {}

    async def cog_check(self, ctx):
        return ctx.guild.id == 696343847210319924

    @commands.command(aliases=['fcount', 'fcounter', 'count'])
    async def counter(self, ctx):
        with open('fcount.json', 'r') as f:
            count = json.load(f)

        await ctx.send(f'Current F counter: {count["count"]}')

    @commands.Cog.listener(name='on_message')
    async def on_grove_message(self, message):
        """Checks for Fs and appends to counter"""
        if not message.guild:
            return

        if message.guild.id != 696343847210319924:
            return

        if message.author.bot:
            return

        cont = ' ' + message.clean_content.lower() + ' '
        if ' f ' not in cont:
            return

        cool = self.cooldowns.get(message.author.id)
        if cool:
            timesince = message.created_at - cool

            if not timesince.seconds:
                return

            if timesince.seconds < 5:
                return

        self.cooldowns[message.author.id] = message.created_at

        with open('fcount.json', 'r') as f:
            count = json.load(f)

        count['count'] += 1

        with open('fcount.json', 'w') as f:
            json.dump(count, f, indent=4)

        botspam = self.bot.get_channel(697218728839872581)
        await botspam.send(f'{message.author.name} paid their respects. Counter: {count["count"]}')


def setup(bot):
    bot.add_cog(groveCog(bot))
