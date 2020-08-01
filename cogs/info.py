import discord
from discord.ext import commands

import time

from .utils import paginator


class infoCog(commands.Cog):
    """Info and Help commands"""

    def __init__(self, bot):
        self.bot = bot
        self.colour = 0xff9300
        self.footer = 'Bot developed by DevilJamJar#0001\nWith a lot of help from ♿nizcomix#7532'
        self.thumb = 'https://styles.redditmedia.com/t5_3el0q/styles/communityIcon_iag4ayvh1eq41.jpg'

    @commands.command()
    async def cogs(self, ctx):
        """≫ Shows all of the bot's cogs"""
        cogs = []
        for cog in self.bot.cogs:
            cogs.append(
                f"`{cog}` • {self.bot.cogs[cog].__doc__}")  # adds cogs and their description to list. if the cog doesnt have a description it will return as "None"
        await ctx.send(embed=discord.Embed(colour=self.colour, title=f"All Cogs ({len(self.bot.cogs)})",
                                           description=f"Do `{ctx.prefix}help <cog>` to know more about them!\nhttps://bit.ly/help-command-by-niztg" + "\n\n" + "\n".join(
                                               cogs)))  # joins each item in the list with a new line

    # ——— This help command was taken from Niz, who made a cool repo for this specifically
    # ——— which you should definitely check out cos it's really awesome and helpful so here's
    # ——— the link https://bit.ly/help-command-by-niztg and go star it or something it's awesome :)

    '''
    @commands.command(aliases=['?'])
    async def help(self, ctx, *, command=None):
        """Shows info about the bot, a command or category"""
        pre = ctx.prefix
        footer = f"Do '{pre}help [command/cog]' for more information!\nhttps://bit.ly/help-command-by-niztg"
        list_of_cogs = []
        walk_commands = []
        final_walk_command_list = []
        sc = []
        format = []
        try:
            for cog in self.bot.cogs:
                list_of_cogs.append(cog)
            if command:
                cmd = self.bot.get_command(command)
            else:
                cmd = None
            if not command:
                k = []
                for cog_name, cog_object in self.bot.cogs.items():
                    cmds = []
                    for cmd in cog_object.get_commands():
                        if not cmd.hidden:
                            cmds.append(f"`{cmd.name}`")
                    k.append(f'➤ **{cog_name}**\n{"•".join(sorted(cmds))}\n')
                for wc in self.bot.walk_commands():
                    if not wc.cog_name and not wc.hidden:
                        if isinstance(wc, commands.Group):
                            walk_commands.append(wc.name)
                            for scw in wc.commands:
                                sc.append(scw.name)
                        else:
                            walk_commands.append(wc.name)
                for item in walk_commands:
                    if item not in final_walk_command_list and item not in sc:
                        final_walk_command_list.append(item)
                for thing in final_walk_command_list:
                    format.append(f"`{thing}`")
                k.append("**➤ Uncategorized Commands**\n" + " • ".join(sorted(format)))
                await ctx.send("** **", embed=discord.Embed(colour=self.colour, title=f"{self.bot.user.name} Help",
                                                            description=f"You can do `{pre}help [category]` for more info on a category.\nYou can also do `{pre}help [command]` for more info on a command.\nhttps://bit.ly/help-command-by-niztg\n\n" + "\n".join(
                                                                k)))
            elif command in list_of_cogs:
                i = []
                cog_doc = self.bot.cogs[command].__doc__ or " "
                for cmd in self.bot.cogs[command].get_commands():
                    if not cmd.aliases:
                        char = "\u200b"
                    else:
                        char = "•"
                    help_msg = cmd.help or "No help provided for this command"
                    i.append(f"→ `{cmd.name}{char}{'•'.join(cmd.aliases)} {cmd.signature}` • {help_msg}")
                await ctx.send(embed=discord.Embed(title=f"{command} Cog", colour=self.colour,
                                                   description=cog_doc + "\n\n" + "\n".join(i)).set_footer(text=footer))
            elif command and cmd:
                help_msg = cmd.help or "No help provided for this command"
                parent = cmd.full_parent_name
                if len(cmd.aliases) > 0:
                    aliases = '•'.join(cmd.aliases)
                    cmd_alias_format = f'{cmd.name}•{aliases}'
                    if parent:
                        cmd_alias_format = f'{parent} {cmd_alias_format}'
                    alias = cmd_alias_format
                else:
                    alias = cmd.name if not parent else f'{parent} {cmd.name}'
                embed = discord.Embed(title=f"{alias} {cmd.signature}", description=help_msg, colour=self.colour)
                embed.set_footer(text=footer)
                if isinstance(cmd, commands.Group):
                    sub_cmds = []
                    for sub_cmd in cmd.commands:
                        schm = sub_cmd.help or "No help provided for this command"
                        if not sub_cmd.aliases:
                            char = "\u200b"
                        else:
                            char = "•"
                        sub_cmds.append(
                            f"→ `{cmd.name} {sub_cmd.name}{char}{'•'.join(sub_cmd.aliases)} {sub_cmd.signature}` • {schm}")
                    scs = "\n".join(sub_cmds)
                    # this is a small work around until I subclass jishaku, don't think much of it please
                    if alias == 'jishaku•jsk':
                        pagey = paginator.MyPaginator(title='Jishaku subcommand help', color=0xff9300, embed=False,
                                                      timeout=90, use_defaults=True,
                                                      entries=[scs[0:1246], scs[1246:2492]], length=1, format='**')

                        await pagey.start(ctx)
                    else:
                        await ctx.send(
                            embed=discord.Embed(title=f"{alias} {cmd.signature}", description=help_msg + "\n\n" + scs,
                                                colour=self.colour).set_footer(text=f"{footer} • → are subcommands"))
                else:
                    await ctx.send(embed=embed)
            else:
                await ctx.send(f"No command named `{command}` found.")
        except Exception as er:
            await ctx.send(er)
    '''

    @commands.command()
    async def ping(self, ctx):
        """Displays latency and response time"""
        begin = time.perf_counter()
        pong = await ctx.send(f'Latency: `{round(self.bot.latency * 1000)}`ms')
        end = time.perf_counter()
        response = round((end - begin) * 1000)
        await pong.edit(content=f'Latency: `{round(self.bot.latency * 1000)}` ms\
                        \nResponse Time: `{response}` ms')

    @commands.command(aliases=['web'])
    async def website(self, ctx):
        """Displays website link"""

        embed = discord.Embed(title='Visit My Website', url='http://overwatchmemesbot.ezyro.com', color=self.colour)
        embed.set_footer(text=self.footer)
        await ctx.send(embed=embed)

    @commands.command(aliases=['inv'])
    async def invite(self, ctx):
        """Displays invite link"""

        embed = discord.Embed(title='Invite me to your server! My default prefix is \'ow!\'',
                              url='https://discord.com/api/oauth2/authorize?client_id=720229743974285312&permissions=2113924179&scope=bot',
                              color=self.colour)
        embed.set_footer(text=self.footer)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(infoCog(bot))
