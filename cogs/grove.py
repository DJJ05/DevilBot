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
        self.poke = {
            'shinx': 370633705091497985,
            'sheinux': 370633705091497985,
            'ralts': 670564722218762240,
            'tralsa': 670564722218762240,
            'solosis': 253223928393236480,
            'monozyto': 253223928393236480,
            'pikachu': 679752282035716115,
            'beldum': 732572646616596480,
            'tanhel': 732572646616596480,
            'gothita': 670373666693054477,
            'mollimorba': 670373666693054477,
            'charmander': 737447606841639044,
            'glumanda': 737447606841639044,
            'sewaddle': 606824731638890528,
            'strawickl': 606824731638890528
        }

    async def cog_check(self, ctx):
        return ctx.guild.id == 696343847210319924

    @commands.Cog.listener(name='on_message')
    async def on_poke_catch(self, message):
        """Catches catches"""
        if not message.guild:
            return
        if message.guild.id != 696343847210319924:
            return
        if message.channel.id != 750463443643007036:
            return
        if message.author.bot:
            return
        cont = message.content.lower()
        if '+c ' not in cont:
            return
        cont = cont.replace('+c ', '')
        if cont not in list(self.poke.keys()):
            return
        member = message.guild.get_member(self.poke[cont])
        if member == message.author:
            return
        ctx = await self.bot.get_context(message)
        await ctx.reply(f'Hey, looks like you caught a **{cont.title()}**.\n\nGood for you, but please check the pins, and next time that Pokémon spawns please ping **{member}**, as that\'s their shiny hunt.\n\nIf you want to start shiny hunting, use `+shinyhunt`.')

    @commands.command(aliases=['fcount', 'fcounter', 'count'])
    async def counter(self, ctx):
        with open('fcount.json', 'r') as f:
            count = json.load(f)

        await ctx.send(f'Current F counter: {count["count"]}')

    @commands.Cog.listener(name='on_message')
    async def on_grove_f(self, message):
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
