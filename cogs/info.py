import collections
import datetime
import os
import pathlib
import time

import discord
import humanize
import psutil
from discord.ext import commands


def linecounter():
    """
    This code was taken from Dutchy#6127 from a
    tag in discord.gg/dpy, called ?tag linecount,
    not sure if it is licensed, but here you go.
    """
    p = pathlib.Path('./')
    cm = cr = fn = cl = ls = fc = 0
    for f in p.rglob('*.py'):
        if str(f).startswith("venv"):
            continue
        fc += 1
        with f.open() as of:
            for l in of.readlines():
                l = l.strip()
                if l.startswith('class'):
                    cl += 1
                if l.startswith('def'):
                    fn += 1
                if l.startswith('async def'):
                    cr += 1
                if '#' in l:
                    cm += 1
                ls += 1
    linecounts = {
        "files": fc,
        "lines": ls,
        "classes": cl,
        "functions": fn,
        "coroutines": cr,
        "comments": cm
    }
    return linecounts


class MyHelpCommand(commands.MinimalHelpCommand):
    async def send_pages(self):
        destination = self.get_destination()
        for page in self.paginator.pages:
            emby = discord.Embed(description=page, colour=0x860111)
            await destination.send(embed=emby)


class infoCog(commands.Cog):
    """Info and Help commands"""

    def __init__(self, bot):
        self.bot = bot
        self._original_help_command = bot.help_command
        bot.help_command = MyHelpCommand()
        bot.help_command.cog = self

        self.footer = 'Bot developed by DevilJamJar#0001\nWith a lot of help from ♿nizcomix#7532'
        self.thumb = 'https://styles.redditmedia.com/t5_3el0q/styles/communityIcon_iag4ayvh1eq41.jpg'

    def cog_unload(self):
        self.bot.help_command = self._original_help_command

    def getproc(self):
        proc = psutil.Process()
        with proc.oneshot():
            mem = proc.memory_full_info()
            physical = humanize.naturalsize(mem.rss)
            virtual = humanize.naturalsize(mem.vms)
            unique = humanize.naturalsize(mem.uss)
            pidname = proc.name()
            pidid = proc.pid
            thread_count = proc.num_threads()
        return {
            'physical': physical,
            'virtual': virtual,
            'unique': unique,
            'pidid': pidid,
            'pidname': pidname,
            'thread_count': thread_count
        }

    @commands.command()
    async def lines(self, ctx):
        """Linecount and much more"""
        linecount = linecounter()
        embed = discord.Embed(
            title='Detailed code overview',
            colour=self.bot.colour
        )
        for key in linecount:
            keyy = key.capitalize()
            embed.add_field(
                name=f'**{keyy}:**',
                value=f'`{linecount.get(key)}`'
            )
        await ctx.send(embed=embed)

    @commands.command(aliases=['info', 'botstats'])
    async def about(self, ctx):
        """All about DevilBot"""
        loop = self.bot.loop
        res = await loop.run_in_executor(None, self.getproc)

        guildpre = ctx.prefix
        appinfo = await self.bot.application_info()
        linecount = linecounter()
        embed = discord.Embed(colour=self.bot.colour,
                              title=f"{appinfo.name} | {appinfo.id}",
                              description=f":diamond_shape_with_a_dot_inside: `Guild Prefix:` **{guildpre}**\
                                        \n<:owner:730864906429136907> `Owner:` **<@!{appinfo.owner.id}>**\
                                        \n\n__**Watching over:**__\
                                        \n+ `Guilds:` **{len(self.bot.guilds)}**\
                                        \n+ `Users:` **{format(len(self.bot.users), ',d')}**\
                                        \n+ `Channels:` **{len(list(self.bot.get_all_channels()))}**\
                                        \n+ `Shards:` **{len(self.bot.shards)}**\
                                        \n\n__**Made with:**__\
                                        \n˚ `Files:` **{linecount['files']}**\
                                        \n˚ `Lines:` **{linecount['lines']:,}**\
                                        \n˚ `Classes:` **{linecount['classes']}**\
                                        \n˚ `Functions:` **{linecount['functions']}**\
                                        \n˚ `Coroutines:` **{linecount['coroutines']}**\
                                        \n˚ `Comments:` **{linecount['comments']}**\
                                        \n\n__**Using:**__\
                                        \n⦿ `Physical Memory:` **{res['physical']}**\
                                        \n⦿ `Virtual Memory:` **{res['virtual']}**\
                                        \n⦿ `Unique Memory:` **{res['unique']}**\
                                        \n⦿ `PID:` **{res['pidname']} {res['pidid']}**\
                                        \n⦿ `Threads:` **{res['thread_count']}**\
                                        \n\n**Do** `{guildpre}help` **to view a full command list.**\
                                        \n**Do** `{guildpre}help [command]` **to view specific command help.**")
        embed.set_author(
            name=f'Requested by {ctx.author}', icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)

    @commands.command(aliases=['server', 'guild'])
    async def support(self, ctx):
        """Support server link"""
        embed = discord.Embed(
            colour=self.bot.colour,
            description='[`Click Me!`](https://discord.gg/KsHgrya)'
        )
        await ctx.send(embed=embed)

    @commands.command()
    async def cogs(self, ctx):
        """Shows all of the bot's cogs"""
        cogs = []
        for cog in self.bot.cogs:
            cogs.append(
                f"`{cog}` • {self.bot.cogs[cog].__doc__}")
        await ctx.send(embed=discord.Embed(colour=self.bot.colour, title=f"All Cogs ({len(self.bot.cogs)})",
                                           description=f"Do `{ctx.prefix}help <cog>` to know more about them!\nhttps://bit.ly/help-command-by-niztg" + "\n\n" + "\n".join(
                                               cogs)))

    @commands.command()
    async def ping(self, ctx):
        """Displays latency and response time"""
        begin = time.perf_counter()
        embed = discord.Embed(
            colour=self.bot.colour, description=f'```json\n"LATENCY": "{round(self.bot.latency * 1000)}ms\n"```')
        pong = await ctx.send(embed=embed)
        end = time.perf_counter()
        response = round((end - begin) * 1000)
        embed = discord.Embed(
            colour=self.bot.colour,
            description=f'```json\n"LATENCY": "{round(self.bot.latency * 1000)}ms"\n"RESPONSE TIME": "{response}ms"```')
        await pong.edit(embed=embed)

    @commands.command(aliases=['inv'])
    async def invite(self, ctx):
        """Displays invite link"""

        embed = discord.Embed(title='Invite me to your server! My default prefix is \'ow!\'',
                              description='__https://discord.com/api/oauth2/authorize?client_id=720229743974285312&permissions=67464257&scope=bot__',
                              color=self.bot.colour)
        await ctx.send(embed=embed)

    @commands.command(aliases=['src'])
    async def source(self, ctx, command: str = None):
        """Shows source code"""
        # Code used from Rapptz' R.Danny repository provided by the MIT License
        # https://github.com/Rapptz/RoboDanny/blob/rewrite/cogs/meta.py#L328-L366
        # Copyright (c) 2015 Rapptz

        # Code used from niztg's CyberTron5000 GitHub Repository Provided by the MIT License
        # https://github.com/niztg/CyberTron5000/blob/master/CyberTron5000/cogs/meta.py#L95-L140
        # Copyright (c) 2020 niztg

        u = '\u200b'
        if not command:
            embed = discord.Embed(title='View my source code on GitHub!', url='https://github.com/DevilJamJar/DevilBot',
                                  colour=self.bot.colour,
                                  description=':scales: `License:` **[Apache-2.0](https://opensource.org/licenses/Apache-2.0)**')
            return await ctx.send(embed=embed)

        if command == 'help':
            embed = discord.Embed(title='View this command on GitHub!',
                                  url='https://github.com/DevilJamJar/DevilBot/blob/master/cogs/info.py#L10-L26',
                                  colour=self.bot.colour,
                                  description=':scales: `License:` **[Apache-2.0](https://opensource.org/licenses/Apache-2.0)**')
            return await ctx.send(embed=embed)

        try:
            src = f"```py\n{str(__import__('inspect').getsource(self.bot.get_command(command).callback)).replace('```', f'{u}')}```"
        except:
            return await ctx.send('Command not found!')
        if len(src) > 2000:
            cmd = self.bot.get_command(command)
            if not cmd:
                return await ctx.send("Command not found.")
            file = cmd.callback.__code__.co_filename
            location = os.path.relpath(file)
            try:
                total, fl = __import__('inspect').getsourcelines(cmd.callback)
            except:
                return await ctx.send('Command not found!')
            ll = fl + (len(total) - 1)
            url = f"https://github.com/DevilJamJar/DevilBot/blob/master/{location}#L{fl}-L{ll}"
            if not cmd.aliases:
                char = '\u200b'
            else:
                char = '/'
            embed = discord.Embed(color=self.bot.colour,
                                  title=f"View this command on GitHub: {cmd.name}{char}{'/'.join(cmd.aliases)}",
                                  url=url)
            embed.description = ":scales: `License:` **[Apache-2.0](https://opensource.org/licenses/Apache-2.0)**"
            await ctx.send(embed=embed)

        else:
            await ctx.send(src)

    @commands.command(aliases=['guildinfo', 'gi', 'si'])
    async def serverinfo(self, ctx):
        '''Get information about the server.'''

        statuses = collections.Counter([m.status for m in ctx.guild.members])

        embed = discord.Embed(colour=self.bot.colour, title=f"{ctx.guild.name}")
        embed.description = ctx.guild.description if ctx.guild.description else None
        embed.add_field(name='**General:**',
                        value=f'Owner: **{ctx.guild.owner}**\n'
                              f'Created on: **{datetime.datetime.strftime(ctx.guild.created_at, "%A %d %B %Y at %H:%M")}**\n'
                              f'<:member:716339965771907099> **{ctx.guild.member_count}**\n'
                              f'<:online:726127263401246832> **{statuses[discord.Status.online]:,}**\n'
                              f'<:idle:726127192165187594> **{statuses[discord.Status.idle]:,}**\n'
                              f'<:dnd:726127192001478746> **{statuses[discord.Status.dnd]:,}**\n'
                              f'<:offline:726127263203983440> **{statuses[discord.Status.offline]:,}**\n'
                              f'<:nitro:731722710283190332> **Tier {ctx.guild.premium_tier}**\n'
                              f'Boosters: **{ctx.guild.premium_subscription_count}**\n'
                              f'Max File Size: **{round(ctx.guild.filesize_limit / 1048576)} MB**\n'
                              f'Bitrate: **{round(ctx.guild.bitrate_limit / 1000)} kbps**\n'
                              f'Max Emojis: **{ctx.guild.emoji_limit}**\n', inline=False)

        embed.add_field(name='**Channel Information:**',
                        value=f'`AFK timeout:` **{int(ctx.guild.afk_timeout / 60)}m**\n'
                              f'`AFK channel:` **{ctx.guild.afk_channel}**\n'
                              f'`Text channels:` **{len(ctx.guild.text_channels)}**\n'
                              f'`Voice channels:` **{len(ctx.guild.voice_channels)}**\n', inline=False)

        embed.set_thumbnail(url=ctx.guild.icon_url)
        embed.set_image(url=ctx.guild.banner_url)
        embed.set_footer(
            text=f'Guild ID: {ctx.guild.id}  |  Requested by: {ctx.author.name}#{ctx.author.discriminator}')

        return await ctx.send(embed=embed)

    @commands.command(aliases=['user', 'ui'])
    async def userinfo(self, ctx, *, member: discord.Member = None):
        '''Get information about a member.'''
        if member is None:
            member = ctx.author
        activity = '`None`'
        if len(member.activities) > 0:
            for activity in member.activities:
                if isinstance(activity, discord.Spotify):
                    activity = 'Listening to `Spotify`'
                elif isinstance(activity, discord.Game):
                    activity = f'Playing `{activity.name}``'
                elif isinstance(activity, discord.Streaming):
                    activity = f'Streaming `{activity.name}`'
        embed = discord.Embed(title=f"{member}", colour=self.bot.colour)
        embed.add_field(name='**General:**',
                        value=f'Name: `{member}`\n'
                              f'Activity: {activity}\n'
                              f'Desktop Status: `{member.desktop_status}`\n'
                              f'Mobile Status: `{member.mobile_status}`\n'
                              f'Browser Status: `{member.web_status}`\n'
                              f'Created on: `{datetime.datetime.strftime(member.created_at, "%A %d %B %Y at %H:%M")}`',
                        inline=False)

        embed.add_field(name='**Guild related information:**',
                        value=f'Joined guild: `{datetime.datetime.strftime(member.joined_at, "%A %d %B %Y at %H:%M")}`\n'
                              f'Nickname: `{member.nick}`\n'
                              f'Top role: {member.top_role.mention}', inline=False)

        embed.set_thumbnail(url=member.avatar_url_as(static_format='png'))
        embed.set_footer(
            text=f'Member ID: {member.id}  |  Requested by: {ctx.author.name}#{ctx.author.discriminator}')

        return await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(infoCog(bot))
