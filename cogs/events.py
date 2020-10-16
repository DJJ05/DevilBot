from discord.ext import commands, tasks
import discord, wikipedia
import json
import traceback
import asyncio
import aiohttp

class eventsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_conn = bot.db_conn

        self.colour = 0xff9300
        self.footer = 'Bot developed by DevilJamJar#0001\nWith a lot of help from ♿nizcomix#7532'
        self.thumb = 'https://styles.redditmedia.com/t5_3el0q/styles/communityIcon_iag4ayvh1eq41.jpg'

        self.btgreen = '\033[1;32m'
        self.tgreen = '\033[32m'
        self.btmag = '\033[1;35m'
        self.tmag = '\033[35m'
        self.btred = '\033[1;31m'
        self.tred = '\033[31m'
        self.endc = '\033[m'

        self.latest = None
        self.durl = 'https://pypi.org/pypi/aiodagpi/json'
        self.checkaiodagpi.start()

    @tasks.loop(seconds=60)
    async def checkaiodagpi(self):
        if not self.latest:
            async with aiohttp.ClientSession() as cs:
                async with cs.get(self.durl) as resp:
                    data = await resp.json()
            await cs.close()
            self.latest = data['info']['version']
            return
        async with aiohttp.ClientSession() as cs:
            async with cs.get(self.durl) as resp:
                data = await resp.json()
        ver = data['info']['version']
        if ver == self.latest:
            return
        self.latest = ver
        git = self.bot.get_channel(745946246371475549)
        desc = ''
        for i in data['info']['classifiers']:
            desc+=f'{i}\n'
        embed=discord.Embed(
            colour=self.colour,
            url=data['info']['package_url'],
            title=f'AioDagpi version {ver} has been released to PyPI!',
            description=f'**Classifiers:**\n{desc}\n**Check it out now and use `pip3 install aiodagpi` to use it :D**'
        )
        embed.set_thumbnail(url='https://static1.squarespace.com/static/59481d6bb8a79b8f7c70ec19/594a49e202d7bcca9e61fe23/59b2ee34914e6b6d89b9241c/1506011023937/pypi_logo.png?format=1500w')
        await git.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        with open('prefixes.json', 'r') as f:
            prefixes = json.load(f)

        prefixes[str(guild.id)] = 'ow!'

        with open('prefixes.json', 'w') as f:
            json.dump(prefixes, f, indent=4)

        c = self.bot.get_channel(745946456946507807)

        embed = discord.Embed(colour=0xff9300, title=f'{guild}',
                              description=f"**{guild.id}**\n**Members: **{len(guild.members)}")
        embed.set_thumbnail(url=guild.icon_url)
        await c.send(f"<@!670564722218762240> We joined guild **#{len(self.bot.guilds)}**", embed=embed)

    @commands.Cog.listener(name="on_message_delete")
    async def on_message_delete(self, message):
        with open('deleted.json', 'r') as f:
            deleted = json.load(f)

        deleted[str(message.channel.id)] = {
            'message': str(message.clean_content),
            'author': str(message.author),
            'created': str(message.created_at)
        }
        await asyncio.sleep(1)

        with open('deleted.json', 'w') as f:
            json.dump(deleted, f, indent=4)

    @commands.Cog.listener(name="on_message")
    async def on_user_mention(self, message):
        if message.content in ("<@!720229743974285312>", "<@720229743974285312>"):
            guildpre = await self.bot.get_prefix(message)
            guildpre = f'{guildpre[2]}'
            appinfo = await self.bot.application_info()
            _commands = []
            for c in self.bot.commands:
                if c.enabled == True:
                    _commands.append(c.name)
            if len(_commands) == len(self.bot.commands):
                currentstatus = f'<:status_online:596576749790429200> `Status:` The Bot is currently **active.**'
            else:
                currentstatus = f'<:status_dnd:596576774364856321> `Status:` The Bot is currently **undergoing maintenance.**'
            embed = discord.Embed(colour=self.colour,
                                  title=f"{appinfo.name} | {appinfo.id}",
                                  description=f":diamond_shape_with_a_dot_inside: `Guild Prefix:` **{guildpre}**\
                                              \n<:owner:730864906429136907> `Owner:` **<@!{appinfo.owner.id}>**\
                                              \n<:text_channel:703726554018086912> `Description:` **{appinfo.description}**\
                                              \n{currentstatus}\
                                              \n\n**Do** `{guildpre}help` **to view a full command list.**\
                                              \n**Do** `{guildpre}help [command]` **to view specific command help.**")
            embed.set_thumbnail(url=self.thumb)
            embed.set_author(name=f'Requested by {message.author.name}#{message.author.discriminator}', icon_url=message.author.avatar_url)
            await message.channel.send(embed=embed)

        # ——————————————————

        if message.guild:
            em = discord.Embed(colour=self.colour, title=f'You may have been mentioned in: {message.guild.name}')
            em.description = f'`Author:` {message.author.mention}\n\
                            `Message:` {message.content}\n\
                            `Created At:` {message.created_at}\n\
                            **[Jump]({message.jump_url})**'
            
            users = {
            'devil': 670564722218762240,
            'freaglii': 370633705091497985,
            'petrick': 370633705091497985,
            'chill': 689912112386277384,
            'para': 596079424680493096,
            'blitz' : 239516219445608449,
            'vic': 595752455409762304,
            'jake' : 116268975020703751,
            'asti' : 517067779145334795
            }
            
            for person in users.keys():
                if person in message.content.lower().replace('\n', ''):
                    if not message.author.bot:
                        if message.guild.id == 621044091056029696:
                            send_to = self.bot.get_user(users.get(person))
                            await send_to.send(embed=em)

            # ——————————————————————————

            with open('afks.json', 'r') as f:
                afks = json.load(f)

            try:
                if afks[str(message.author.id)]:

                    #replace the time with python struct, i forgot how it works sorry
                    longmess = int(int(str(message.created_at).split(" ")[1].replace(":", ".").replace(".", "")) - int(afks[str(message.author.id)]["time"])) / 1000000
                    min, sec = divmod(longmess, 60) 
                    hour, min = divmod(min, 60) 
                    finalmess = "%d:%02d:%02d" % (hour, min, sec)
                    await message.channel.send(f'{message.author.mention}, I removed your AFK')
                    afks.pop(str(message.author.id))
                    with open('afks.json', 'w') as f:
                        json.dump(afks, f, indent=4)
                    
            except KeyError:
                pass

            # —————————————————————————
            
            if len(message.mentions):
                with open('afks.json', 'r') as f:
                    afks = json.load(f)
                for i in message.mentions:
                    if str(i.id) in afks and message.author != message.guild.me:
                        await message.channel.send(f'**{message.author.mention},** `{i.display_name} is currently AFK.`\n**Reason:** `{afks[str(i.id)]["message"]}`')

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        with open('prefixes.json', 'r') as f:
            prefixes = json.load(f)

        prefixes.pop(str(guild.id))

        with open('prefixes.json', 'w') as f:
            json.dump(prefixes, f, indent=4)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        # Error formatting code used from Daggy1234's DagBot GitHub Repository Provided by the GNU Affero General
        # Public License @ https://github.com/Daggy1234/dagbot/blob/master/dagbot/extensions/errors.py#L37-#L42
        # Copyright (C) 2020  Daggy1234
        
        etype = type(error)
        trace = error.__traceback__
        verbosity = 4
        lines = traceback.format_exception(etype, error, trace, verbosity)
        traceback_text = f'```py\n{"".join(lines)}\n```'

        embyw = discord.Embed(colour=self.colour)
        embyw.set_thumbnail(url='https://cdn.discordapp.com/attachments/745950521072025714/766734683479998574/attention.png')

        embye = discord.Embed(colour=self.colour)
        embye.set_thumbnail(url='https://cdn.discordapp.com/attachments/745950521072025714/766734680371888128/warning.png')

        if etype == commands.CommandNotFound:
            return

        elif etype == commands.DisabledCommand:
            embyw.title = 'This command is disabled!'
            embyw.description = f'{ctx.author.mention}, `{ctx.prefix}{ctx.command.qualified_name}` has been **temporarily** disabled by my owner. Please check back later.'
            await ctx.send(embed=embyw)

        elif etype == commands.TooManyArguments:
            embyw.title = 'You gave me too much info!'
            embyw.description = f'{ctx.author.mention}, you gave me arguments (values *after* {ctx.prefix}{ctx.command.qualified_name}) that I wasn\'t ready for. Please check the usage with {ctx.prefix}help {ctx.command.qualified_name}.'
            await ctx.send(embed=embyw)

        elif etype == commands.BadUnionArgument or etype == commands.ConversionError:
            embye.title = 'Couldn\'t convert to object!'
            embye.description = f'{ctx.author.mention}, I couldn\'t convert the given argument(s) into objects. This means that I couldn\'t locate the given member, guild, channel etc. Check for typos!'
            await ctx.send(embed=embye)

        elif etype == commands.BadArgument:
            embye.title = 'Faulty information detected!'
            embye.description = f'{ctx.author.mention}, you gave me faulty information! This may mean that a member, guild, channel etc. that I was supposed to use could not be located. Check for typos!'
            await ctx.send(embed=embye)

        elif etype == commands.MemberNotFound:
            embyw.title = 'Member not found!'
            embyw.description = f'{ctx.author.mention}, the member you told me to find ({error.argument}) could not be located! Check for typos.'
            await ctx.send(embed=embyw)

        elif etype == commands.CommandOnCooldown:
            seconds = error.retry_after
            seconds = round(seconds, 2)
            remainder = divmod(int(seconds), 3600)
            minutes, seconds = divmod(remainder, 60)
            embyw.title = 'You are on cooldown!'
            embyw.description = f'{ctx.author.mention}, you are still on cooldown for a remaining `{minutes} minutes and {seconds} seconds!` Cool it down.'
            await ctx.send(embed=embyw)

        elif etype == commands.MaxConcurrencyReached:
            embyw.title = 'This command is too powerful for me!'
            embyw.description = f'{ctx.author.mention}, this command is too powerful for me and has been limited to only `{error.number}` uses running at the same time in `{str(error.per)}`.'
            await ctx.send(embed=embyw)

        elif etype == commands.NotOwner:
            embyw.title = 'This command is restricted!'
            embyw.description = f'{ctx.author.mention}, this command contains power too immense for you, and has been limited to only my owner! Come back when you own me.'
            await ctx.send(embed=embyw)

        elif etype == commands.NSFWChannelRequired:
            embye.title = 'This command is NSFW locked!'
            embye.description = f'{ctx.author.mention}, the channel #{error.channel.name} is not marked NSFW, which this command requires. If you are a moderator, please mark this channel as such!'
            await ctx.send(embed=embye)

        elif etype == commands.MissingRole:
            embyw.title = 'You are missing a role!'
            embyw.description = f'{ctx.author.mention}, you are missing a role required to perform this command: {error.missing_role.name}. Check your role list!'
            await ctx.send(embed=embyw)

        elif etype == commands.MissingPermissions:
            embyw.title = 'You are missing permissions!'
            embyw.description = f'{ctx.author.mention}, you are missing permissions required to perform this command: {error.missing_perms}. Check your permissions!'
            await ctx.send(embed=embyw)

        elif etype == commands.BotMissingRole:
            embyw.title = 'I am missing a role!'
            embyw.description = f'{ctx.author.mention}, I am missing a role required to perform this command: {error.missing_role.name}. Check my roles!'
            await ctx.send(embed=embyw)

        elif etype == commands.BotMissingPermissions:
            embyw.title = 'I am missing permissions!'
            embyw.description = f'{ctx.author.mention}, I am missing permissions required to perform this command: {error.missing_perms}. Check my permissions!'
            await ctx.send(embed=embyw)

        elif etype == commands.MissingRequiredArgument:
            embyw.title = 'You forgot to fill in the blanks!'
            embyw.description = f'{ctx.author.mention}, you didn\'t enter the required argument: {error.param.name}.'
            await ctx.send(embed=embyw)

        else:
            print(f'{self.btred} ERROR: {self.tred} {traceback_text} {self.endc}——————————————————————————————')
            embed = discord.Embed(colour=0xff0033, title=f'Error during `{ctx.command.name}`',
                                  description=f'ID: {ctx.message.id}\nMy creator has been notified of the error and will endeavour to fix it soon.\n{traceback_text}')
            await ctx.send(embed=embed)

            errchannel = self.bot.get_channel(748962623487344753)

            embed = discord.Embed(colour=0xff0033, title=f'Error during `{ctx.command.name}`',
                                  description=f'ID: {ctx.message.id}\n[Jump]({ctx.message.jump_url})\n{traceback_text}')
            a = await errchannel.send(embed=embed)

            with open('errors.json', 'r') as f:
                errors = json.load(f)

            errors[str(ctx.message.id)] = {
                "traceback":traceback_text,
                "command":ctx.command.name,
                "author":ctx.author.id,
                "errormessage":a.id,
                "followers":[]
            }

            with open('errors.json', 'w') as f:
                json.dump(errors, f, indent=4)

def setup(bot):
    bot.add_cog(eventsCog(bot))
