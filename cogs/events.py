import asyncio
import json

import discord
from discord.ext import commands


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

        c = self.bot.get_channel(745946456946507807)

        embed = discord.Embed(colour=0xff9300, title=f'{guild}',
                              description=f"**{guild.id}**\
                              \n**Members:** {len(guild.members)}\
                              \n**Region:** {str(guild.region).capitalize()}\
                              \n**Owner: ** {guild.owner}")
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
    async def on_message(self, message):
        if message.content in ("<@!720229743974285312>", "<@720229743974285312>"):
            guildpre = await self.bot.get_prefix(message)
            guildpre = f'{guildpre[2]}'
            appinfo = await self.bot.application_info()
            _commands = []
            for c in self.bot.commands:
                if c.enabled:
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
            embed.set_author(
                name=f'Requested by {message.author.name}#{message.author.discriminator}',
                icon_url=message.author.avatar_url)
            await message.channel.send(embed=embed)

        #  ——————————————————

        if message.guild:
            em = discord.Embed(
                colour=self.colour, title=f'You may have been mentioned in: {message.guild.name}')
            em.description = f'`Author:` {message.author.mention}\n\
                            `Message:` {message.content}\n\
                            `Created At:` {message.created_at}\n\
                            **[Jump]({message.jump_url})**'

            users = {
                ' devil ': 670564722218762240,
                ' freaglii ': 370633705091497985,
                ' petrick ': 370633705091497985,
                ' chill ': 689912112386277384,
                ' para ': 596079424680493096,
                ' blitz ': 239516219445608449,
                ' vic ': 595752455409762304,
                ' jake ': 116268975020703751,
                'asti ': 517067779145334795
            }

            concac = ' ' + message.content.lower().replace('\n', '') + ' '
            for person in users.keys():
                if person in concac:
                    if not message.author.bot:
                        if message.guild.id == 621044091056029696:
                            send_to = self.bot.get_user(users.get(person))
                            await send_to.send(embed=em)
                        elif message.guild.id == 696343847210319924 and person == ' jake ':
                            send_to = self.bot.get_user(users.get(person))
                            await send_to.send(embed=em)

            # ——————————————————————————

            with open('afks.json', 'r') as f:
                afks = json.load(f)

            try:
                if afks[str(message.author.id)]:
                    # replace the time with python struct, i forgot how it works sorry
                    longmess = int(int(str(message.created_at).split(" ")[1].replace(":", ".").replace(
                        ".", "")) - int(afks[str(message.author.id)]["time"])) / 1000000
                    _min, sec = divmod(longmess, 60)
                    hour, _min = divmod(_min, 60)
                    finalmess = "%d:%02d:%02d" % (hour, _min, sec)
                    await message.channel.send(f'{message.author.mention}, I removed your AFK', delete_after=5)
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
                        await message.channel.send(
                            f'**{message.author.mention},** `{i.display_name} is currently AFK.`\n**Reason:** `{afks[str(i.id)]["message"]}`',
                            delete_after=5)

            # —————————————————————————

            if message.guild.id == 696343847210319924 and message.author.id == 716390085896962058 and len(message.embeds) > 0:
                if message.embeds[0].title == 'A wild pokémon has appeared!':
                    owner = self.bot.get_user(670564722218762240)
                    emby = discord.Embed(
                        title='New Pokémon spawn in the Grove.',
                        description=f'[Message URL]({message.jump_url})',
                        colour=self.colour
                    )
                    await owner.send(embed=emby)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        with open('prefixes.json', 'r') as f:
            prefixes = json.load(f)

        prefixes.pop(str(guild.id))

        with open('prefixes.json', 'w') as f:
            json.dump(prefixes, f, indent=4)

    '''@commands.Cog.listener()
    async def on_message_edit(self, before, after):
        await self.bot.process_commands(after)'''


def setup(bot):
    bot.add_cog(eventsCog(bot))
