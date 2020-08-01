from discord.ext import commands
import discord
import json
import traceback

class eventsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_conn = bot.db_conn

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

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        with open('prefixes.json', 'r') as f:
            prefixes = json.load(f)

        prefixes.pop(str(guild.id))

        with open('prefixes.json', 'w') as f:
            json.dump(prefixes, f, indent=4)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        _raise = [
            commands.CheckFailure,
            commands.NotOwner
        ]

        skip = [
            commands.CommandNotFound
        ]

        disabled = [
            commands.DisabledCommand
        ]

        if type(error) in skip:
            return
        elif type(error) in _raise:
            return await ctx.send(f'<@!{ctx.author.id}>, something went wrong.\n`{error}`')
        elif type(error) in disabled:
            return await ctx.send(f':warning: <@!{ctx.author.id}> The bot is currently in `maintenance mode.`\nThis means I\'m working on fixing bugs or imperfections and don\'t want you breaking anything. Please be patient.')
        else:
            print(f'An uncaught error occured during the handling of a command, {type(error)} » {error}')
            return await ctx.send(f'<@!{ctx.author.id}>, something went wrong that I wasn\'t expecting. The error has been sent to my owner.\n`{error}`')

def setup(bot):
    bot.add_cog(eventsCog(bot))
