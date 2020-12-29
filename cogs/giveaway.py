# -*- coding: utf-8 -*-

import asyncio
import datetime
import discord
import random
import re
import json

from discord.ext import commands, tasks
from discord.ext.commands.cooldowns import BucketType

from .utils import checks

time_regex = re.compile("(?:(\d{1,5})(h|s|m|d|w))+?")
time_dict = {"h": 3600, "s": 1, "m": 60, "d": 86400, "w": 604800}


class TimeConverter(commands.Converter):
    async def convert(self, ctx, argument):
        args = argument.lower()
        matches = re.findall(time_regex, args)
        time = 0
        for v, k in matches:
            try:
                time += time_dict[k] * float(v)
            except KeyError:
                raise commands.BadArgument(f"{k} is an invalid time-key! h/m/s/d are valid!")
            except ValueError:
                raise commands.BadArgument(f"{v} is not a number!")
        return [argument, time]


class giveawayCog(commands.Cog):
    """Giveaway commands"""

    def __init__(self, bot):
        self.bot = bot
        self.db_conn = bot.db_conn
        self.colour = 0xff9300
        self.get_giveaways.start()

    @tasks.loop(seconds=30)
    async def get_giveaways(self):
        if not self.bot:
            return
        await self.bot.wait_until_ready()
        with open('giveaways.json', 'r') as f:
            data = json.load(f)
        if not len(data.keys()):
            return
        finished = []
        for guild_id, contents in data.items():
            for chan_id, inside in contents.items():
                ends = datetime.datetime.strptime(inside['ends'], '%c')
                now = datetime.datetime.utcnow()
                if now >= ends:
                    finished.append(guild_id)
                    guild = self.bot.get_guild(int(guild_id))
                    channel = self.bot.get_channel(int(chan_id))
                    await channel.send('The giveaway has ended! Randomly drawing winner...')
                    entries = inside['entries']
                    if not len(entries):
                        await channel.send('The giveaway had no entries...')
                        break
                    while True:
                        try:
                            user = random.choice(entries)
                        except:
                            await channel.send('All users that entered the giveaway have left the guild...')
                            break
                        member = guild.get_member(user)
                        if not member:
                            await channel.send('Randomly drawn user has left the guild. Redrawing...')
                            entries.remove(user)
                        else:
                            await channel.send(f'The randomly selected winner is **{member.mention}**! Well done and thank you for entering!')
                            break
        for id_ in finished:
            data.pop(id_)
        with open('giveaways.json', 'w') as f:
            json.dump(data, f, indent=4)

    @commands.Cog.listener(name='on_raw_reaction_add')
    async def catch_entries(self, payload):
        """Catche entries and enters them"""
        if not payload.member:
            return
        if payload.member.bot:
            return
        with open('giveaways.json', 'r') as f:
            data = json.load(f)
        gwjs = data.get(str(payload.guild_id))
        if gwjs is None:
            return
        gwch = gwjs.get(str(payload.channel_id))
        if gwch is None:
            return
        if str(gwch['message']) != str(payload.message_id):
            return
        embed = discord.Embed(
            title=f'✨ You entered the giveaway! ✨',
            colour=self.colour,
            description=f'Ends: __{datetime.datetime.strptime(gwch["ends"], "%c").strftime("%c")}__'
        )
        dact = data[str(payload.guild_id)][str(payload.channel_id)]['entries']
        if payload.member.id in dact:
            return
        dact.append(payload.member.id)
        await payload.member.send(embed=embed)
        with open('giveaways.json', 'w') as f:
            json.dump(data, f, indent=4)

    @commands.Cog.listener(name='on_raw_reaction_remove')
    async def catch_del_entries(self, payload):
        """Catche removed entries and delete them"""
        user = await self.bot.fetch_user(payload.user_id)
        with open('giveaways.json', 'r') as f:
            data = json.load(f)
        gwjs = data.get(str(payload.guild_id))
        if gwjs is None:
            return
        gwch = gwjs.get(str(payload.channel_id))
        if gwch is None:
            return
        if str(gwch['message']) != str(payload.message_id):
            return
        embed = discord.Embed(
            title=f'You left the giveaway...',
            colour=self.colour,
            description=f'Ends: __{datetime.datetime.strptime(gwch["ends"], "%c").strftime("%c")}__'
        )
        dact = data[str(payload.guild_id)][str(payload.channel_id)]['entries']
        if user.id not in dact:
            return
        dact.remove(user.id)
        await user.send(embed=embed)
        with open('giveaways.json', 'w') as f:
            json.dump(data, f, indent=4)

    @commands.group(invoke_without_command=True)
    @checks.check_admin_or_owner()
    async def giveaway(self, ctx):
        """Giveaway command group, requires administrator permissions to create a giveaway"""
        await ctx.send_help(ctx.command)

    @giveaway.command()
    @commands.max_concurrency(1, BucketType.channel)
    async def create(self, ctx, giveaway_length: TimeConverter, *, prize: str):
        """Creates a giveaway"""
        if giveaway_length[1] > 2628288:
            cancelled = await ctx.send(
                f'{ctx.author.mention}, sorry. Giveaways cannot be longer than 1 month. These messages will delete in 10 seconds.')
            await asyncio.sleep(10)
            await cancelled.delete()
            try:
                await ctx.message.delete()
            except:
                ...

        def check(m):
            return m.channel.id == ctx.channel.id and m.author.id == ctx.author.id

        ending_at = ctx.message.created_at + datetime.timedelta(seconds=giveaway_length[1])
        ending_at_pretty = ending_at.strftime('%c')

        try:
            timeconfirm = await ctx.send(
                f'Please say "yes" to confirm you wish to create a giveaway ending at `{ending_at_pretty} UTC`. You have 60 seconds.')
            msg2 = await self.bot.wait_for('message', check=check, timeout=60)
        except asyncio.TimeoutError:
            cancelled = await ctx.send(
                f'{ctx.author.mention}, you took too long. These messages will delete in 10 seconds.')
            await asyncio.sleep(10)
            for deleteable in [timeconfirm, cancelled]:
                await deleteable.delete()
            try:
                await ctx.message.delete()
                await msg2.delete()
                return
            except:
                return
        if not msg2.content.lower() == 'yes':
            cancelled = await ctx.send(f'{ctx.author.mention}, cancelled. These messages will delete in 10 seconds.')
            await asyncio.sleep(10)
            for deleteable in [timeconfirm, cancelled]:
                await deleteable.delete()
            try:
                await ctx.message.delete()
                await msg2.delete()
            except:
                ...
            return

        with open('giveaways.json', 'r') as f:
            data = json.load(f)

        if data.get(str(ctx.guild.id)) is not None:
            return await ctx.send(f'{ctx.author.mention} There\'s already an ongoing giveaway in this guild!')

        embed = discord.Embed(
            colour=random.choice([0xFF7D00, 0xFF006D, 0xFFDD00, 0x01BEFE, 0xADFF02, 0x8F00FF]),
            title=f'✨  **{prize}**  ✨',
            description=f'React with <a:enter:788138546040274944> to enter!\nEnds: __{ending_at_pretty} UTC__',
            timestamp=ctx.message.created_at
        )
        embed.set_thumbnail(url='https://cdn0.iconfinder.com/data/icons/small-n-flat/24/678132-gift-512.png')
        embed.set_author(icon_url=str(ctx.author.avatar_url), name=ctx.author.name)
        embed.set_footer(text='Created:')
        giveaway = await ctx.send('--------–– **GIVEAWAY** ------––––', embed=embed)
        try:
            await giveaway.add_reaction('<a:enter:788138546040274944>')
        except:
            await ctx.send('I tried reacting but I couldn\'t!')

        data[ctx.guild.id] = {
            ctx.channel.id: {
                'message': giveaway.id,
                'creator': ctx.author.id,
                'ends': str(ending_at_pretty),
                'started': str(ctx.message.created_at),
                'entries': []
            }
        }

        with open('giveaways.json', 'w') as f:
            json.dump(data, f, indent=4)

        await timeconfirm.delete()
        try:
            await ctx.message.delete()
            await msg2.delete()
        except:
            ...


def setup(bot):
    bot.add_cog(giveawayCog(bot))
