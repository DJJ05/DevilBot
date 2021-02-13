# -*- coding: utf-8 -*-

import sys
import traceback

import discord
from discord.ext import commands


class eh(commands.Cog):
    """Error handler"""
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """Command error listener"""
        if isinstance(ctx.channel, discord.DMChannel):
            return

        if hasattr(ctx.command, 'on_error'):
            return

        ignored = (commands.CommandNotFound,)
        error = getattr(error, 'original', error)

        if isinstance(error, ignored):
            return

        if isinstance(error, commands.DisabledCommand):
            await ctx.send(f'{str(ctx.command).capitalize()} has been disabled by my owner. Please check back later.')

        elif isinstance(error, commands.NoPrivateMessage):
            try:
                await ctx.author.send(f'{ctx.command} cannot be used in Private Messages. Please use it in your guild.')
            except discord.HTTPException:
                pass

        elif isinstance(error, commands.BadArgument):
            await ctx.send('\n'.join(error.args))

        elif isinstance(error, commands.TooManyArguments):
            await ctx.send('\n'.join(error.args))

        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('\n'.join(error.args))

        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send('\n'.join(error.args))

        elif isinstance(error, commands.MaxConcurrencyReached):
            await ctx.send('\n'.join(error.args))

        elif isinstance(error, commands.CheckFailure):
            if 'The check functions for command' in error.args[0]:
                return
            await ctx.send('\n'.join(error.args))

        elif isinstance(error, discord.Forbidden):
            await ctx.send('\n'.join(error.args))

        else:
            print('Ignoring exception in command {}:'.format(
                ctx.command), file=sys.stderr)
            traceback.print_exception(
                type(error), error, error.__traceback__, file=sys.stderr)

            etype = type(error)
            trace = error.__traceback__
            verbosity = 2
            lines = traceback.format_exception(etype, error, trace, verbosity)
            traceback_text = f'```py\n{"".join(lines)}\n```'.replace(
                'rajsharma', 'dev')

            embed = discord.Embed(title=f'Error during `{ctx.command.qualified_name}`',
                                  description=f'ID: {ctx.message.id}\n[Jump]({ctx.message.jump_url})\n\
                                                {traceback_text}')

            lines = traceback.format_exception(etype, error, trace, 1)
            traceback_text = f'```py\n{"".join(lines)}\n```'.replace(
                'rajsharma', 'dev')
            embed.description = f'ID: {ctx.message.id}\n[Jump]({ctx.message.jump_url})\n{traceback_text}'
            await ctx.send(embed=embed)


def setup(bot):
    """Setup func"""
    bot.add_cog(eh(bot))
