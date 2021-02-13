# -*- coding: utf-8 -*-

import traceback

import discord
from discord.ext import commands
from wikipedia.exceptions import DisambiguationError


class errorhandler(commands.Cog):
    """Error handler cog"""

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(ctx.channel, discord.DMChannel):
            return

        if hasattr(ctx.command, 'on_error'):
            return

        ignored = (commands.CommandNotFound,)
        error = getattr(error, 'original', error)

        if isinstance(error, ignored):
            return

        user_err = (
            commands.DisabledCommand,
            commands.BadArgument,
            commands.TooManyArguments,
            commands.MissingRequiredArgument,
            commands.CommandOnCooldown,
            commands.MaxConcurrencyReached,
            commands.CheckFailure,
            DisambiguationError,
            discord.Forbidden
        )

        if isinstance(error, user_err):
            await ctx.send('\n'.join(error.args))

        else:
            self.bot.logger.error(f'Ignoring exception in command {ctx.command}:')

            etype = type(error)
            trace = error.__traceback__
            lines = traceback.format_exception(etype, error, trace, 3)
            lines = "".join(lines).strip('\n')

            self.bot.logger.error(lines)

            lines = traceback.format_exception(etype, error, trace, 1)
            traceback_text = f'```py\n{"".join(lines)}\n```'.replace(
                'rajsharma', 'dev')
            embed = discord.Embed(title=f'Error during `{ctx.command.qualified_name}`',
                                  colour=self.bot.colour,
                                  description=f'ID: {ctx.message.id}\n[Jump]({ctx.message.jump_url})\n\
                                                            {traceback_text}')
            embed.description = f'ID: {ctx.message.id}\n[Jump]({ctx.message.jump_url})\n{traceback_text}'
            await ctx.reply(embed=embed)


def setup(bot):
    bot.add_cog(errorhandler(bot))
