from discord.ext import commands
import discord, wikipedia
import json
import traceback

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

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        with open('prefixes.json', 'r') as f:
            prefixes = json.load(f)

        prefixes[str(guild.id)] = 'ow!'

        with open('prefixes.json', 'w') as f:
            json.dump(prefixes, f, indent=4)

        a = sorted([c for c in guild.text_channels if c.permissions_for(guild.me).send_messages],
                   key=lambda x: x.position)
        channel = a[0]
        inv = await channel.create_invite()
        finalinv = f"https://discord.gg/{inv.code}"

        c = self.bot.get_channel(715744000077725769)

        embed = discord.Embed(colour=0xff9300, title=f'{guild}',
                              description=f"**{guild.id}**\n**{finalinv}**")
        embed.set_thumbnail(url=guild.icon_url)
        await c.send(f"<@!670564722218762240> We joined guild **#{len(self.bot.guilds)}**", embed=embed)

    @commands.Cog.listener(name="on_message_delete")
    async def on_message_delete(self, message):
        with open('deleted.json', 'r') as f:
            deleted = json.load(f)

        deleted[str(message.channel.id)] = f'{message.clean_content} ««« {message.author.name}#{message.author.discriminator} ««« {message.created_at}'

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
            'para ': 596079424680493096,
            'blitz': 239516219445608449,
            }
            
            for person in users.keys():
                if person in message.content.lower().replace('\n', '') and message.author.id != 720229743974285312:
                    send_to = self.bot.get_user(users.get(person))
                    await send_to.send(embed=em)
                    
            def check(message):
                return message.author.id not in (517067779145334795, 720229743974285312) and message.guild.id == 621044091056029696
                
            if 'asti ' in message.content.lower() or 'mos ' in message.content.lower() and check(message):
                asti = self.bot.get_user(517067779145334795)
                await asti.send(embed=em)

            # ——————————————————————————

            with open('afks.json', 'r') as f:
                afks = json.load(f)

            try:
                if afks[str(message.author.id)]:

                    #replace the time with python struct, i forgot how it works sorry
                    await message.channel.send(f'{message.author.mention}, I removed your AFK. You were in afk for {(afks[str(message.author.id)]["time"] - message.created_at)/60} mins')
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
                    if str(i.id) in afks:
                        await message.channel.send(f'**{message.author.mention},** `{i.display_name} is currently AFK.`\n**Reason:** `{afks[str(i.id)].capitalize()}`')

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        with open('prefixes.json', 'r') as f:
            prefixes = json.load(f)

        prefixes.pop(str(guild.id))

        with open('prefixes.json', 'w') as f:
            json.dump(prefixes, f, indent=4)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        # Code used from Daggy1234's DagBot GitHub Repository Provided by the GNU Affero General Public License
        # https://github.com/Daggy1234/dagbot/blob/master/dagbot/extensions/errors.py#L37-#L42
        # Copyright (C) 2020  Daggy1234
        
        etype = type(error)
        trace = error.__traceback__
        verbosity = 4
        lines = traceback.format_exception(etype, error, trace, verbosity)
        traceback_text = f'```py\n{"".join(lines)}\n```'

        _raise = [
            commands.NotOwner,
            commands.MissingRequiredArgument,
            commands.BadArgument,
            commands.CommandOnCooldown,
            commands.MaxConcurrencyReached,
            commands.BadUnionArgument
        ]

        skip = [
            commands.CommandNotFound
        ]

        disabled = [
            commands.DisabledCommand
        ]

        checks = [
            commands.CheckFailure
        ]

        if type(error) in skip:
            return
        elif type(error) in _raise:
            return await ctx.send(f':warning: {ctx.author.mention}, a `known error` occured.\n`{error}`')
        elif type(error) in checks:
            return await ctx.send(f':warning: {ctx.author.mention}, you failed to meet the checks required for this command.\nThis may be because you are not `the owner`, in the `correct guild`, or missing `required roles or permissions.`')
        elif type(error) in disabled:
            return await ctx.send(f':warning: {ctx.author.mention}, I am currently in `maintenance mode`. Please be patient, I will be fixed soon!')
        else:
            print(f'{self.btred} ERROR: {self.tred} {traceback_text} {self.endc}——————————————————————————————')
            embed = discord.Embed(colour=0xff0033, title=f'Error during `{ctx.command.name}`',
                                  description=f'ID: {ctx.message.id}\nMy creator has been notified of the error and will endeavour to fix it soon.\n{traceback_text}')
            await ctx.send(embed=embed)
            await ctx.send(f'If you would like to receive updates on this error, use `{ctx.prefix}error follow {ctx.message.id}`')

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
