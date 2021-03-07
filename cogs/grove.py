# -*- coding: utf-8 -*-

import json
import textwrap

import aiohttp
import discord
from PIL import Image, ImageFont, ImageDraw
from discord.ext import commands


def add_silly_text(text):
    image = Image.open("silly.png")
    wrapped = textwrap.wrap(text, width=45)
    font = ImageFont.truetype('Locanita.ttf', 150)
    editable = ImageDraw.Draw(image)

    offset = 65
    for line in wrapped:
        editable.text((500, offset), line, (255, 255, 255), font=font)
        offset += font.getsize(line)[1]

    image.save("sillyfinal.png")


class groveCog(commands.Cog):
    """Grove-only commands"""

    def __init__(self, bot):
        self.bot = bot

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
        return ctx.guild.id in (696343847210319924, 688817596250062850)

    @commands.command(aliases=['mc'])
    async def grove(self, ctx):
        """Grove MC server info"""
        async with aiohttp.ClientSession() as c, ctx.typing():
            async with c.get('https://api.mcsrvstat.us/2/mc.gaminggrove.tk') as r:
                res = await r.json()

            if not res['online']:
                return await ctx.reply('The server is not online.')

            embed = discord.Embed(
                colour=self.bot.colour,
                title=res['hostname'],
                description=res['motd']['clean'][0]
            )
            if res['players'].get('list'):
                players = res['players']['list'][:5]
            else:
                players = []
                res['players']['list'] = []
            more = 0
            if len(players) < len(res['players']['list']):
                more = len(res['players']['list']) - len(players)
            if not len(players):
                player_str = 'None'
            else:
                player_first = '\n'.join([f'• {n}' for n in players])
                player_str = f"{player_first}\n{f'And {more} more...' if more != 0 else ''}"
            embed.add_field(name='Online', value=player_str, inline=False)
            embed.add_field(name='Max', value=res['players']['max'])
            embed.add_field(name='Version', value=res['version'], inline=True)
            embed.add_field(name='Software', value=res['software'], inline=True)
            return await ctx.reply(embed=embed)

    @commands.command()
    async def silly(self, ctx, *, text):
        async with ctx.typing():
            await self.bot.loop.run_in_executor(None, add_silly_text, text)
            file = discord.File("sillyfinal.png", filename="silly_says.png")
        await ctx.reply(file=file)

    @commands.command(aliases=['ac'])
    async def awesomecat(self, ctx):
        await ctx.send('https://cdn.discordapp.com/attachments/443522014934859787/805496748218384475/image0-13.gif')

    @commands.command(aliases=['gabe'])
    async def zex(self, ctx):
        await ctx.reply('https://cdn.discordapp.com/attachments/696343847764230147/816598764751683594/unknown.png')

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
        await ctx.reply(
            f'Hey, looks like you caught a **{cont.title()}**.\n\nGood for you, but please check the pins, and next time that Pokémon spawns please ping **{member}**, as that\'s their shiny hunt.\n\nIf you want to start shiny hunting, use `+shinyhunt`.')

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
