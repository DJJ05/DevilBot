# -*- coding: utf-8 -*-

import discord
from discord.ext import commands
import json

from .utils import checks


class starboardCog(commands.Cog):
    """Starboard commands"""

    def __init__(self, bot):
        self.bot = bot
        self.db_conn = bot.db_conn
        self.colour = 0xff9300

    @commands.Cog.listener(name='on_raw_reaction_add')
    async def on_star_add(self, payload):
        """Catches star reactions and incremements / adds message to starboard"""
        if not payload.member:
            return
        if payload.member.bot:
            return
        if str(payload.emoji) != '⭐':
            return

        guild = self.bot.get_guild(payload.guild_id)
        channel = guild.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        member = payload.member

        with open('starboard.json', 'r') as f:
            data = json.load(f)

        if not data.get(str(guild.id)):
            return

        if message.author == member:
            return
        if message.author.bot:
            return
        if len(message.embeds) > 0:
            return

        starboard = guild.get_channel(data[str(guild.id)]["channel"])

        if data[str(guild.id)]["messages"].get(str(message.id)) is not None:
            data[str(guild.id)]["messages"][str(message.id)]["stars"] += 1
            if data[str(guild.id)]["messages"][str(message.id)]["embed"] is not None:
                msg = await starboard.fetch_message(data[str(guild.id)]["messages"][str(message.id)]["embed"])
                await msg.edit(content=f'**{data[str(guild.id)]["messages"][str(message.id)]["stars"]}** :star:')
        else:
            data[str(guild.id)]["messages"][str(message.id)] = {
                "stars": 1,
                "channel": channel.id,
                "embed": None
            }

        if data[str(guild.id)]["messages"][str(message.id)]["stars"] == data[str(guild.id)]["stars"]:
            embed = discord.Embed(
                colour=self.colour,
                description=message.content,
                timestamp=message.created_at
            )
            embed.add_field(name='Original', value=f'[Jump!]({message.jump_url})')
            embed.set_author(name=message.author.name, icon_url=message.author.avatar_url)
            if len(message.attachments) > 0:
                try:
                    embed.set_image(url=message.attachments[0].url)
                except:
                    pass
            msg = await starboard.send(f'**{data[str(guild.id)]["stars"]}** :star:', embed=embed)
            data[str(guild.id)]["messages"][str(message.id)]["embed"] = msg.id

        with open('starboard.json', 'w') as f:
            json.dump(data, f, indent=4)

    @commands.Cog.listener(name='on_raw_reaction_remove')
    async def on_star_remove(self, payload):
        """Catches star removals and decrements / removes message from starboard"""
        guild = self.bot.get_guild(payload.guild_id)
        channel = guild.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        member = guild.get_member(payload.user_id)

        if member.bot:
            return
        if str(payload.emoji) != '⭐':
            return

        with open('starboard.json', 'r') as f:
            data = json.load(f)

        if not data.get(str(guild.id)):
            return

        if message.author == member:
            return
        if message.author.bot:
            return
        if len(message.embeds) > 0:
            return

        starboard = guild.get_channel(data[str(guild.id)]["channel"])

        if data[str(guild.id)]["messages"].get(str(message.id)) is not None:
            data[str(guild.id)]["messages"][str(message.id)]["stars"] -= 1
            if data[str(guild.id)]["messages"][str(message.id)]["embed"] is not None:
                msg = await starboard.fetch_message(data[str(guild.id)]["messages"][str(message.id)]["embed"])
                if data[str(guild.id)]["messages"][str(message.id)]["stars"] < data[str(guild.id)]["stars"]:
                    await msg.delete()
                    data[str(guild.id)]["messages"][str(message.id)]["embed"] = None
                else:
                    await msg.edit(content=f'**{data[str(guild.id)]["messages"][str(message.id)]["stars"]}** :star:')

        with open('starboard.json', 'w') as f:
            json.dump(data, f, indent=4)

    @commands.group(invoke_without_command=True)
    @checks.check_admin_or_owner()
    async def starboard(self, ctx):
        """Starboard command group, see subcommands for setup. Requires administrator."""
        await ctx.send_help(ctx.command)

    @starboard.command(aliases=['lb'])
    async def leaderboard(self, ctx):
        """Displays a leaderboard from most to least stars per person"""
        people = {}

        with open('starboard.json', 'r') as f:
            data = json.load(f)

        if data.get(str(ctx.guild.id)) is None:
            raise commands.BadArgument(
                f'There is no starboard in this server. Use `{ctx.prefix}starboard create` to create one.')

        if len(list(data[str(ctx.guild.id)]["messages"].keys())) < 1:
            raise commands.BadArgument('There have been so stars in this server.')

        for m_id, inside in data[str(ctx.guild.id)]["messages"].items():
            channel = ctx.guild.get_channel(inside["channel"])
            msg = await channel.fetch_message(int(m_id))
            if people.get(str(msg.author)) is not None:
                people[str(msg.author)] += inside["stars"]
            else:
                people[str(msg.author)] = inside["stars"]

        people = dict(sorted(people.items(), key=lambda item: item[1], reverse=True))
        people = {x: people[x] for x in list(people.keys)[:10]}

        leaderboard = ''
        lbnum = 1

        for person, stars in people.items():
            leaderboard += f'{lbnum}) **{person[:-5]}** – {stars} :star:'
            lbnum += 1

        embed = discord.Embed(
            colour=self.colour,
            title='Star Leaderboard',
            description=leaderboard,
            timestamp=ctx.message.created_at
        )

        return await ctx.reply(embed=embed)

    @starboard.command(aliases=['star'])
    @checks.check_admin_or_owner()
    async def stars(self, ctx, minimum_star_count: int = 4):
        """Sets the minimum star count of a guild to a new value greater than 0. Defaults to 4."""
        with open('starboard.json', 'r') as f:
            data = json.load(f)

        if data.get(str(ctx.guild.id)) is None:
            raise commands.BadArgument(
                f'There is no starboard in this server. Use `{ctx.prefix}starboard create` to create one.')

        if minimum_star_count < 1:
            raise commands.BadArgument('You need a minimum number greater than 0.')

        old = data[str(ctx.guild.id)]["stars"]
        data[str(ctx.guild.id)]["stars"] = minimum_star_count

        with open('starboard.json', 'w') as f:
            json.dump(data, f, indent=4)

        if minimum_star_count < old:
            return await ctx.reply('Done.')
        if len(list(data[str(ctx.guild.id)]["messages"].keys())) < 1:
            return await ctx.reply('Done.')

        await ctx.reply('Purging messages that do not fit the new requirement...')
        starboard = ctx.guild.get_channel(data[str(ctx.guild.id)]["channel"])

        for msg_id, inside in data[str(ctx.guild.id)]["messages"].items():
            if inside["stars"] < minimum_star_count and inside["embed"]:
                msg = await starboard.fetch_message(inside["embed"])
                await msg.delete()
                inside["embed"] = None

        with open('starboard.json', 'w') as f:
            json.dump(data, f, indent=4)

        return await ctx.reply('Done.')

    @starboard.command(aliases=['stop', 'exit', 'cancel'])
    @checks.check_admin_or_owner()
    async def close(self, ctx):
        """Closes an active starboard, but DOES NOT delete the channel. Bot will simply stop tracking stars."""
        with open('starboard.json', 'r') as f:
            data = json.load(f)

        if data.get(str(ctx.guild.id)) is None:
            raise commands.BadArgument(
                f'There is no starboard in this server. Use `{ctx.prefix}starboard create` to create one.')

        data.pop(str(ctx.guild.id))

        with open('starboard.json', 'w') as f:
            json.dump(data, f, indent=4)

        await ctx.reply('Done.')

    @starboard.command(aliases=['make', 'start'])
    @checks.check_admin_or_owner()
    async def create(self, ctx, channel: discord.TextChannel, minimum_star_count: int = 5):
        """Creates an active starboard in a specified channel, with specified minimum star count. Bot requires send_messages permissions in starboard channel, and it is recommended to disallow @ everyone from talking there."""
        if minimum_star_count < 1:
            raise commands.BadArgument('You need a minimum number greater than 0.')

        with open('starboard.json', 'r') as f:
            data = json.load(f)

        if data.get(str(ctx.guild.id)) is not None:
            raise commands.BadArgument(
                f'There is already a starboard in this server. Use `{ctx.prefix}starboard close` to remove it.')

        if not channel.permissions_for(ctx.me).send_messages:
            raise commands.BadArgument(f'I need send_messages permissions in {channel.mention} to send messages there.')

        data[str(ctx.guild.id)] = {
            "channel": channel.id,
            "stars": minimum_star_count,
            "messages": {}
        }

        with open('starboard.json', 'w') as f:
            json.dump(data, f, indent=4)

        return await ctx.reply(
            f'Alright, I activated a starboard in {channel.mention} with a minimum star count of {minimum_star_count}. The allowed emoji is :star: and bots, self-starrers and embeds are not allowed to star. Use `{ctx.prefix}starboard` to view all of the available config commands.')


def setup(bot):
    bot.add_cog(starboardCog(bot))
