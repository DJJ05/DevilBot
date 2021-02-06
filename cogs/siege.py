# -*- coding: utf-8 -*-

import r6sapi
import discord
from discord.ext import commands
from .secrets import secrets_siege_email, secrets_siege_password


class siegeCog(commands.Cog):
    """Rainbow 6 commands"""

    def __init__(self, bot):
        self.bot = bot
        self.colour = 0xff9300
        self.auth = r6sapi.Auth(secrets_siege_email, secrets_siege_password)

    @commands.group(invoke_without_command=True)
    async def siege(self, ctx):
        """Siege command group, see subcommands for help."""
        await ctx.send_help(ctx.command)

    @siege.command(aliases=['pi', 'playerinfo', 'account', 'accountinfo'])
    async def player(self, ctx, account_name):
        """Information about a siege Uplay account."""
        try:
            account = await self.auth.get_player(account_name, r6sapi.Platforms.UPLAY)
        except r6sapi.exceptions.InvalidRequest:
            raise commands.BadArgument("Couldn't find a Uplay account with that name.")
        embed = discord.Embed(
            colour=self.colour,
            title=account.name,
            description=account.userid,
            url=account.url
        )
        try:
            await account.check_level()
            await account.check_general()
            await account.check_queues()
        except:
            raise commands.BadArgument("Found the Uplay account but couldn't gather any information.")
        embed.add_field(name='Level', value=f'{account.level:,}')
        embed.add_field(name='Platform', value=account.platform)
        embed.add_field(name='Xp', value=f'{account.xp:,}')
        embed.add_field(name='Kills', value=f'{account.kills:,}')
        embed.add_field(name='Deaths', value=f'{account.deaths:,}')
        embed.add_field(name='Revives', value=f'{account.revives:,}')
        embed.add_field(name='Matches Played', value=f'{account.matches_played:,}')
        embed.add_field(name='Matches Won', value=f'{account.matches_won:,}')
        embed.add_field(name='Matches lost', value=f'{account.matches_lost:,}')
        embed.add_field(name='Bullets Fired', value=f'{account.bullets_fired:,}')
        embed.add_field(name='Bullets Hit', value=f'{account.bullets_hit:,}')
        embed.add_field(name='Headshots', value=f'{account.headshots:,}')
        embed.add_field(name='Ranked Games', value=f'{account.ranked.played:,}')
        embed.add_field(name='Casual Games', value=f'{account.casual.played:,}')
        embed.add_field(name='Kill Assists', value=f'{account.kill_assists:,}')
        embed.set_thumbnail(url=account.icon_url)
        await ctx.reply(embed=embed)

def setup(bot):
    bot.add_cog(siegeCog(bot))
