# -*- coding: utf-8 -*-

import json

import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType

from .utils import checks


class starboardCog(commands.Cog):
    """Starboard commands"""

    def __init__(self, bot):
        self.bot = bot
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
        skip = False

        res = await self.bot.db.starboard.find_one({"guild": guild.id})

        if not res:
            return
        if message.author.bot:
            return
        if len(message.embeds) > 0:
            return

        starboard = guild.get_channel(res["channel"])

        if message.author == member:
            if res["messages"].get(str(message.id)) is not None:
                res["messages"][str(message.id)]["stars"] -= 1
                if res["messages"][str(message.id)]["embed"] is not None:
                    msg = await starboard.fetch_message(res["messages"][str(message.id)]["embed"])
                    if res["messages"][str(message.id)]["stars"] < res["stars"]:
                        await msg.delete()
                        res["messages"][str(message.id)]["embed"] = None
                    else:
                        await msg.edit(
                            content=f'**{res["messages"][str(message.id)]["stars"]}** :star:')
            else:
                res["messages"][str(message.id)] = {
                    "stars": -1,
                    "channel": channel.id,
                    "embed": None
                }
            skip = True

        if skip is not True:
            if res["messages"].get(str(message.id)) is not None:
                res["messages"][str(message.id)]["stars"] += 1
                if res["messages"][str(message.id)]["embed"] is not None:
                    msg = await starboard.fetch_message(res["messages"][str(message.id)]["embed"])
                    await msg.edit(content=f'**{res["messages"][str(message.id)]["stars"]}** :star:')
            else:
                res["messages"][str(message.id)] = {
                    "stars": 1,
                    "channel": channel.id,
                    "embed": None
                }

            if res["messages"][str(message.id)]["stars"] == res["stars"]:
                embed = discord.Embed(
                    colour=self.colour,
                    description=message.content if len(message.content) > 0 else '\u200b',
                    timestamp=message.created_at
                )
                embed.add_field(name='Original', value=f'[Jump!]({message.jump_url})')
                embed.set_author(name=message.author.name, icon_url=message.author.avatar_url)
                if len(message.attachments) > 0:
                    if message.attachments[0].filename[-4:] in ('.png', '.jpg', '.jpeg', '.gif'):
                        embed.set_image(url=message.attachments[0].url)
                        msg = await starboard.send(f'**{res["stars"]}** :star:', embed=embed)
                    else:
                        attach = message.attachments[0]
                        file = await attach.to_file()
                        msg = await starboard.send(f'**{res["stars"]}** :star:', embed=embed, file=file)
                else:
                    msg = await starboard.send(
                        f'**{res["messages"][str(message.id)]["stars"]}** :star:',
                        embed=embed)
                res["messages"][str(message.id)]["embed"] = msg.id

        await self.bot.db.starboard.update_one(
            {"guild": guild.id},
            {"$set": {"messages": res["messages"]}}
        )

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

        res = await self.bot.db.starboard.find_one({"guild": guild.id})

        if not res:
            return

        if message.author == member:
            return
        if message.author.bot:
            return

        starboard = guild.get_channel(res["channel"])

        if res["messages"].get(str(message.id)) is not None:
            res["messages"][str(message.id)]["stars"] -= 1
            if res["messages"][str(message.id)]["embed"] is not None:
                msg = await starboard.fetch_message(res["messages"][str(message.id)]["embed"])
                if res["messages"][str(message.id)]["stars"] < res["stars"]:
                    await msg.delete()
                    res["messages"][str(message.id)]["embed"] = None
                else:
                    await msg.edit(content=f'**{res["messages"][str(message.id)]["stars"]}** :star:')

        await self.bot.db.starboard.update_one(
            {"guild": guild.id},
            {"$set": {"messages": res["messages"]}}
        )

    @commands.group(invoke_without_command=True)
    @checks.check_admin_or_owner()
    async def starboard(self, ctx):
        """Starboard command group, see subcommands for setup. Requires administrator."""
        await ctx.send_help(ctx.command)

    @starboard.command()
    @checks.check_admin_or_owner()
    @commands.cooldown(1, 30, BucketType.user)
    async def update(self, ctx, message: discord.Message, star_count: int):
        """Updates the star count of a message with a new star count. This is updated internally, so keep in mind that the message reaction count and the stars in the starboard channel may not match. You must be in the same channel as the original message to use this command."""
        async with ctx.typing():
            res = await self.bot.db.starboard.find_one({"guild": ctx.guild.id})

            if not res:
                raise commands.BadArgument(
                    f"There is no starboard in this server. Use `{ctx.prefix}starboard create` to create one.")

            if message.author.bot:
                raise commands.BadArgument('Bots are hard configured to be ignored by the starbord.')

            starboard = ctx.guild.get_channel(res["channel"])

            if res["messages"].get(str(message.id)) is not None:
                res["messages"][str(message.id)]["stars"] = star_count

                if res["messages"][str(message.id)]["embed"] is not None:
                    msg = await starboard.fetch_message(res["messages"][str(message.id)]["embed"])

                    if res["messages"][str(message.id)]["stars"] < res["stars"]:
                        await msg.delete()
                        res["messages"][str(message.id)]["embed"] = None

                    else:
                        await msg.edit(
                            content=f'**{res["messages"][str(message.id)]["stars"]}** :star:')
                else:
                    if res[str(ctx.guild.id)]["messages"][str(message.id)]["stars"] >= res["stars"]:
                        embed = discord.Embed(
                            colour=self.colour,
                            description=message.content if len(message.content) > 0 else '\u200b',
                            timestamp=message.created_at
                        )
                        embed.add_field(name='Original', value=f'[Jump!]({message.jump_url})')
                        embed.set_author(name=message.author.name, icon_url=message.author.avatar_url)

                        if len(message.attachments) > 0:
                            if message.attachments[0].filename[-4:] in ('.png', '.jpg', '.jpeg', '.gif'):
                                embed.set_image(url=message.attachments[0].url)
                                msg = await starboard.send(
                                    f'**{res["messages"][str(message.id)]["stars"]}** :star:',
                                    embed=embed)
                            else:
                                try:
                                    attach = message.attachments[0]
                                    file = await attach.to_file()
                                    msg = await starboard.send(f'**{res["stars"]}** :star:', embed=embed, file=file)
                                except:
                                    msg = await starboard.send(f'**{res["stars"]}** :star:', embed=embed)
                        else:
                            msg = await starboard.send(
                                f'**{res["messages"][str(message.id)]["stars"]}** :star:',
                                embed=embed)

                        res["messages"][str(message.id)]["embed"] = msg.id
            else:
                res["messages"][str(message.id)] = {
                    "stars": star_count,
                    "channel": message.channel.id,
                    "embed": None
                }
                if res["messages"][str(message.id)]["stars"] >= res["stars"]:
                    embed = discord.Embed(
                        colour=self.colour,
                        description=message.content if len(message.content) > 0 else '\u200b',
                        timestamp=message.created_at
                    )
                    embed.add_field(name='Original', value=f'[Jump!]({message.jump_url})')
                    embed.set_author(name=message.author.name, icon_url=message.author.avatar_url)

                    if len(message.attachments) > 0:
                        if message.attachments[0].filename[-4:] in ('.png', '.jpg', '.jpeg', '.gif'):
                            embed.set_image(url=message.attachments[0].url)
                            msg = await starboard.send(
                                f'**{res["messages"][str(message.id)]["stars"]}** :star:', embed=embed)
                        else:
                            attach = message.attachments[0]
                            file = await attach.to_file()
                            msg = await starboard.send(f'**{res["stars"]}** :star:', embed=embed,
                                                       file=file)
                    else:
                        msg = await starboard.send(
                            f'**{res["messages"][str(message.id)]["stars"]}** :star:',
                            embed=embed)

                    res["messages"][str(message.id)]["embed"] = msg.id

            await self.bot.db.starboard.update_one(
                {"guild": ctx.guild.id},
                {"$set": {"messages": res["messages"]}}
            )

        return await ctx.reply("Updated star count successfully.")

    @starboard.command(aliases=['lb'])
    async def leaderboard(self, ctx):
        """Displays a leaderboard from most to least stars per person"""
        async with ctx.typing():
            people = {}

            res = await self.bot.db.starboard.find_one({"guild": ctx.guild.id})

            if not res:
                raise commands.BadArgument(
                    f"There is no starboard in this server. Use `{ctx.prefix}starboard create` to create one.")

            if len(list(res["messages"].keys())) < 1:
                raise commands.BadArgument('There have been so stars in this server.')

            for m_id, inside in res["messages"].items():
                try:
                    channel = ctx.guild.get_channel(inside["channel"])
                    msg = await channel.fetch_message(int(m_id))
                    if people.get(str(msg.author)) is not None:
                        people[str(msg.author)] += inside["stars"]
                    else:
                        people[str(msg.author)] = inside["stars"]
                except:
                    pass

            people = dict(sorted(people.items(), key=lambda item: item[1], reverse=True))
            people = {x: people[x] for x in list(people.keys())[:10]}

            leaderboard = ''
            lbnum = 1

            for person, stars in people.items():
                leaderboard += f'{lbnum}) **{person[:-5]}** – {stars} :star:\n'
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
        async with ctx.typing():
            res = await self.bot.db.starboard.find_one({"guild": ctx.guild.id})

            if not res:
                raise commands.BadArgument(
                    f"There is no starboard in this server. Use `{ctx.prefix}starboard create` to create one.")

            if minimum_star_count < 1:
                raise commands.BadArgument('You need a minimum number greater than 0.')

            old = res["stars"]

            if minimum_star_count < old:
                await ctx.reply('Done.')

            if len(list(res["messages"].keys())) < 1:
                await ctx.reply('Done.')

            else:
                await ctx.reply('Purging messages that do not fit the new requirement...')
                starboard = ctx.guild.get_channel(res["channel"])

                for msg_id, inside in res["messages"].items():
                    if inside["stars"] < minimum_star_count and inside["embed"]:
                        try:
                            msg = await starboard.fetch_message(inside["embed"])
                            await msg.delete()
                            res["messages"][msg_id]["embed"] = None
                        except discord.NotFound:
                            pass

            await self.bot.db.starboard.update_one(
                {"guild": ctx.guild.id},
                {"$set": {"stars": minimum_star_count, "messages": res["messages"]}}
            )

            return await ctx.reply('Done.')

    @starboard.command(aliases=['stop', 'exit', 'cancel'])
    @checks.check_admin_or_owner()
    async def close(self, ctx):
        """Closes an active starboard, but DOES NOT delete the channel. Bot will simply stop tracking stars."""
        async with ctx.typing():
            res = await self.bot.db.starboard.find_one({"guild": ctx.guild.id})

            if not res:
                raise commands.BadArgument(
                    f"There is no starboard in this server. Use `{ctx.prefix}starboard create` to create one.")

            await ctx.reply('Removed starboard.')

        await self.bot.db.starboard.delete_one({"guild": ctx.guild.id})

    @starboard.command(aliases=['make', 'start'])
    @checks.check_admin_or_owner()
    async def create(self, ctx, channel: discord.TextChannel, minimum_star_count: int = 5):
        """Creates an active starboard in a specified channel, with specified minimum star count. Bot requires send_messages permissions in starboard channel, and it is recommended to disallow @ everyone from talking there."""
        async with ctx.typing():
            if minimum_star_count < 1:
                raise commands.BadArgument('You need a minimum number greater than 0.')

            res = await self.bot.db.starboard.find_one({"guild": ctx.guild.id})

            if res:
                raise commands.BadArgument(f"There is already a starboard in this server. Use `{ctx.prefix}starboard close` to remove it.")

            if not channel.permissions_for(ctx.me).send_messages:
                raise commands.BadArgument(f'I need send_messages permissions in {channel.mention} to send messages there.')

            to_insert = {
                "guild": ctx.guild.id,
                "channel": channel.id,
                "stars": minimum_star_count,
                "messages": {}
            }

            await self.bot.db.starboard.insert_one(to_insert)

        return await ctx.reply(
            f'Alright, I activated a starboard in {channel.mention} with a minimum star count of {minimum_star_count}. The allowed emoji is :star: and bots, self-starrers and embeds are not allowed to star. Use `{ctx.prefix}starboard` to view all of the available config commands.')


def setup(bot):
    bot.add_cog(starboardCog(bot))
