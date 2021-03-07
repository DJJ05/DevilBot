# -*- coding: utf-8 -*-

import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType

from .utils import checks


class starboardcog(commands.Cog):
    """Starboard cog"""

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener(name='on_raw_reaction_add')
    async def on_star_add(self, payload):
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

        if message.author == member:
            return

        res = await self.bot.db.starboard_config.find_one({"_id": guild.id}, max_time_ms=20000)

        if not res:
            return
        if message.author.bot:
            return

        starboard = guild.get_channel(res["channel"])

        _msg = await self.bot.db.starboard.find_one({"_id": message.id}, max_time_ms=20000)

        if _msg is not None:
            _msg["stars"] += 1
            if _msg["embed"] is not None:
                try:
                    msg = await starboard.fetch_message(_msg["embed"])
                    await msg.edit(content=f'**{_msg["stars"]}** :star:')
                except:
                    pass
        else:
            _msg = {
                "guild": guild.id,
                "_id": message.id,
                "stars": 1,
                "channel": message.channel.id,
                "embed": None
            }

        if _msg["stars"] >= res["stars"] and _msg["embed"] is None:
            embed = discord.Embed(
                colour=self.bot.colour,
                description=message.content if len(message.content) > 0 else '\u200b',
                timestamp=message.created_at
            )
            embed.add_field(name='Original', value=f'[Jump!]({message.jump_url})')
            embed.set_author(name=message.author.name, icon_url=message.author.avatar_url)
            if len(message.attachments) > 0:
                if message.attachments[0].filename[-4:] in ('.png', '.jpg', '.jpeg', '.gif'):
                    embed.set_image(url=message.attachments[0].url)
                    msg = await starboard.send(f'**{_msg["stars"]}** :star:', embed=embed)
                else:
                    attach = message.attachments[0]
                    file = await attach.to_file()
                    msg = await starboard.send(f'**{_msg["stars"]}** :star:', embed=embed, file=file)
            else:
                msg = await starboard.send(
                    f'**{_msg["stars"]}** :star:',
                    embed=embed)
            _msg["embed"] = msg.id

        await self.bot.db.starboard.update_one(
            {"_id": message.id},
            {"$set": {"guild": _msg["guild"], "_id": _msg["_id"], "stars": _msg["stars"], "channel": _msg["channel"],
                      "embed": _msg["embed"]}},
            upsert=True
        )

    @commands.Cog.listener(name='on_raw_reaction_remove')
    async def on_star_remove(self, payload):
        guild = self.bot.get_guild(payload.guild_id)
        channel = guild.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        member = guild.get_member(payload.user_id)

        if member.bot:
            return
        if str(payload.emoji) != '⭐':
            return

        res = await self.bot.db.starboard_config.find_one({"_id": guild.id}, max_time_ms=20000)

        if not res:
            return

        if message.author == member:
            return
        if message.author.bot:
            return

        starboard = guild.get_channel(res["channel"])

        _msg = await self.bot.db.starboard.find_one({"_id": message.id}, max_time_ms=20000)

        if _msg is not None:
            _msg["stars"] -= 1
            if _msg["embed"] is not None:
                try:
                    msg = await starboard.fetch_message(_msg["embed"])
                    if _msg["stars"] < res["stars"]:
                        await msg.delete()
                        _msg["embed"] = None
                    else:
                        await msg.edit(content=f'**{_msg["stars"]}** :star:')
                except:
                    pass

            await self.bot.db.starboard.update_one(
                {"_id": message.id},
                {"$set": {"stars": _msg["stars"], "embed": _msg["embed"]}}
            )

    @commands.group(invoke_without_command=True)
    @checks.check_admin_or_owner()
    async def starboard(self, ctx):
        """Returns subcommands"""
        await ctx.send_help(ctx.command)

    @starboard.command()
    @checks.check_admin_or_owner()
    @commands.cooldown(1, 30, BucketType.user)
    async def update(self, ctx, message: discord.Message, star_count: int):
        """Updates star count of messages"""
        async with ctx.typing():
            res = await self.bot.db.starboard_config.find_one({"_id": ctx.guild.id}, max_time_ms=20000)

            if not res:
                raise commands.BadArgument(
                    f"There is no starboard in this server. Use `{ctx.prefix}starboard create` to create one.")

            if message.author.bot:
                raise commands.BadArgument('Bots are hard configured to be ignored by the starbord.')

            starboard = ctx.guild.get_channel(res["channel"])

            _msg = await self.bot.db.starboard.find_one({"_id": message.id}, max_time_ms=20000)

            if _msg is not None:
                _msg["stars"] = star_count

                if _msg["embed"] is not None:
                    try:
                        msg = await starboard.fetch_message(_msg["embed"])

                        if _msg["stars"] < res["stars"]:
                            await msg.delete()
                            _msg["embed"] = None
                    except:
                        pass

                    else:
                        await msg.edit(
                            content=f'**{_msg["stars"]}** :star:')
                else:
                    if _msg["stars"] >= res["stars"]:
                        embed = discord.Embed(
                            colour=self.bot.colour,
                            description=message.content if len(message.content) > 0 else '\u200b',
                            timestamp=message.created_at
                        )
                        embed.add_field(name='Original', value=f'[Jump!]({message.jump_url})')
                        embed.set_author(name=message.author.name, icon_url=message.author.avatar_url)

                        if len(message.attachments) > 0:
                            if message.attachments[0].filename[-4:] in ('.png', '.jpg', '.jpeg', '.gif'):
                                embed.set_image(url=message.attachments[0].url)
                                msg = await starboard.send(
                                    f'**{_msg["stars"]}** :star:',
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
                                f'**{_msg["stars"]}** :star:',
                                embed=embed)

                        _msg["embed"] = msg.id
            else:
                _msg = {
                    "guild": ctx.guild.id,
                    "_id": message.id,
                    "stars": star_count,
                    "channel": message.channel.id,
                    "embed": None
                }
                if _msg["stars"] >= res["stars"]:
                    embed = discord.Embed(
                        colour=self.bot.colour,
                        description=message.content if len(message.content) > 0 else '\u200b',
                        timestamp=message.created_at
                    )
                    embed.add_field(name='Original', value=f'[Jump!]({message.jump_url})')
                    embed.set_author(name=message.author.name, icon_url=message.author.avatar_url)

                    if len(message.attachments) > 0:
                        if message.attachments[0].filename[-4:] in ('.png', '.jpg', '.jpeg', '.gif'):
                            embed.set_image(url=message.attachments[0].url)
                            msg = await starboard.send(
                                f'**{_msg["stars"]}** :star:', embed=embed)
                        else:
                            attach = message.attachments[0]
                            file = await attach.to_file()
                            msg = await starboard.send(f'**{res["stars"]}** :star:', embed=embed,
                                                       file=file)
                    else:
                        msg = await starboard.send(
                            f'**{_msg["stars"]}** :star:',
                            embed=embed)

                    _msg["embed"] = msg.id

            await self.bot.db.starboard.update_one(
                {"_id": message.id},
                {"$set": {"guild": _msg["guild"], "_id": _msg["_id"], "stars": _msg["stars"],
                          "channel": _msg["channel"],
                          "embed": _msg["embed"]}},
                upsert=True
            )

        return await ctx.reply("Updated star count successfully.")

    @starboard.command(aliases=['lb'])
    async def leaderboard(self, ctx):
        """Returns collected starcount leaderboard"""
        async with ctx.typing():
            people = {}

            res = await self.bot.db.starboard_config.find_one({"_id": ctx.guild.id}, max_time_ms=20000)

            if not res:
                raise commands.BadArgument(
                    f"There is no starboard in this server. Use `{ctx.prefix}starboard create` to create one.")

            try:
                messages = self.bot.db.starboard.find({"guild": ctx.guild.id})
                messages = await messages.to_list(length=None)
            except:
                return await ctx.reply('Couldn\'t find any starred messages from this guild.')
            if len(messages) < 1:
                return await ctx.reply('Couldn\'t find any starred messages from this guild.')

            for _msg in messages:
                try:
                    channel = ctx.guild.get_channel(_msg["channel"])
                    msg = await channel.fetch_message(int(_msg['_id']))
                    if people.get(str(msg.author)) is not None:
                        people[str(msg.author)] += _msg["stars"]
                    else:
                        people[str(msg.author)] = _msg["stars"]
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
                colour=self.bot.colour,
                title='Star Leaderboard',
                description=leaderboard,
                timestamp=ctx.message.created_at
            )

        return await ctx.reply(embed=embed)

    @starboard.command(aliases=['star'])
    @checks.check_admin_or_owner()
    async def stars(self, ctx, minimum_star_count: int = 4):
        """Updates the minimum stars required for a starboard entry"""
        async with ctx.typing():
            res = await self.bot.db.starboard_config.find_one({"_id": ctx.guild.id}, max_time_ms=20000)

            if not res:
                raise commands.BadArgument(
                    f"There is no starboard in this server. Use `{ctx.prefix}starboard create` to create one.")

            if minimum_star_count < 1:
                raise commands.BadArgument('You need a minimum number greater than 0.')

            old = res["stars"]

            if minimum_star_count < old:
                await ctx.reply('Done.')

            else:
                try:
                    messages = self.bot.db.starboard.find({"guild": ctx.guild.id})
                    messages = await messages.to_list(length=None)
                except:
                    return await ctx.reply('Done.')
                if len(messages) < 1:
                    return await ctx.reply('Done.')

                await ctx.reply('Purging messages that do not fit the new requirement...')
                starboard = ctx.guild.get_channel(res["channel"])

                for _msg in messages:
                    if _msg["stars"] < minimum_star_count and _msg["embed"]:
                        try:
                            msg = await starboard.fetch_message(_msg["embed"])
                            await msg.delete()
                            _msg["embed"] = None
                            await self.bot.db.starboard.update_one(
                                {"_id": _msg["_id"]},
                                {"$set": {"embed": None}}
                            )
                        except:
                            pass

            await self.bot.db.starboard_config.update_one(
                {"_id": ctx.guild.id},
                {"$set": {"stars": minimum_star_count}}
            )

        return await ctx.reply('Done.')

    @starboard.command(aliases=['stop', 'exit', 'cancel'])
    @checks.check_admin_or_owner()
    async def close(self, ctx):
        """Removes an active starboard"""
        async with ctx.typing():
            res = await self.bot.db.starboard_config.find_one({"_id": ctx.guild.id}, max_time_ms=20000)

            if not res:
                raise commands.BadArgument(
                    f"There is no starboard in this server. Use `{ctx.prefix}starboard create` to create one.")

            await self.bot.db.starboard_config.delete_one({"_id": ctx.guild.id})

        await ctx.reply('Removed starboard.')

    @starboard.command(aliases=['make', 'start'])
    @checks.check_admin_or_owner()
    async def create(self, ctx, channel: discord.TextChannel, minimum_star_count: int = 5):
        """Creates an active starboard"""
        async with ctx.typing():
            if minimum_star_count < 1:
                raise commands.BadArgument('You need a minimum number greater than 0.')

            res = await self.bot.db.starboard_config.find_one({"_id": ctx.guild.id}, max_time_ms=20000)

            if res:
                raise commands.BadArgument(
                    f"There is already a starboard in this server. Use `{ctx.prefix}starboard close` to remove it.")

            if not channel.permissions_for(ctx.me).send_messages:
                raise commands.BadArgument(
                    f'I need send_messages permissions in {channel.mention} to send messages there.')

            to_insert = {
                "_id": ctx.guild.id,
                "channel": channel.id,
                "stars": minimum_star_count
            }

            await self.bot.db.starboard_config.insert_one(to_insert)

        return await ctx.reply(
            f'Alright, I activated a starboard in {channel.mention} with a minimum star count of {minimum_star_count}. The allowed emoji is :star: and bots, self-starrers and embeds are not allowed to star. Use `{ctx.prefix}starboard` to view all of the available config commands.')


def setup(bot):
    bot.add_cog(starboardcog(bot))
