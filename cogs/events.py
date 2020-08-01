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
        perms = [
            commands.NotOwner,
            commands.MissingPermissions,
            commands.MissingRole
        ]

        skip = [
            commands.CommandNotFound
        ]

        if type(error) in skip:
            return
        elif type(error) in perms:
            return await ctx.send(f'<@!{ctx.author.id}>, you are missing the required permissions for that\n`{error}`')
        else:
            print(f'An uncaught error occured during the handling of a command, {type(error)} » {error}')

def setup(bot):
    bot.add_cog(eventsCog(bot))
