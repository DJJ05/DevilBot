import discord
from discord.ext import commands

import os

class devCog(commands.Cog):
    """Developer commands"""

    def __init__(self, bot):
        self.bot = bot
        self.db_conn = bot.db_conn
        self.colour = 0xff9300
        self.footer = 'Bot developed by DevilJamJar#0001\nWith a lot of help from ♿nizcomix#7532'
        self.thumb = 'https://styles.redditmedia.com/t5_3el0q/styles/communityIcon_iag4ayvh1eq41.jpg'

    @commands.command(aliases=['tm'])
    @commands.is_owner()
    async def ToggleMaintenance(self, ctx):
        """Toggles bot maintenance mode"""
        for c in self.bot.commands:
            if c.name != 'ToggleMaintenance':
                if c.enabled == False:
                    c.enabled = True
                else:
                    c.enabled = False
        print('Maintenance has been toggled.')
        return await ctx.send('Successfully `toggled` maintenance mode.')

    @commands.command()
    @commands.is_owner()
    async def load(self, ctx, extension:str=None):
        """Loads a cog."""
        if extension:
            self.bot.load_extension(f'cogs.{extension}')
            return await ctx.send(f'Successfully loaded extension `cogs.{extension}.`')

    @commands.command()
    @commands.is_owner()
    async def unload(self, ctx, extension:str=None):
        """Unloads a cog."""
        if extension:
            self.bot.unload_extension(f'cogs.{extension}')
            return await ctx.send(f'Successfully unloaded extension `cogs.{extension}.`')

    @commands.command()
    @commands.is_owner()
    async def reload(self, ctx, extension:str=None):
        """Reloads all cogs or a specified cog"""
        if not extension:
            for filename in os.listdir('./cogs'):
                if filename.endswith('.py') and filename != 'dev.py':
                    self.bot.unload_extension(f'cogs.{filename[:-3]}')
                    self.bot.load_extension(f'cogs.{filename[:-3]}')
            return await ctx.send('Successfully reloaded extension `all cogs.`')
        self.bot.unload_extension(f'cogs.{extension}')
        self.bot.load_extension(f'cogs.{extension}')
        return await ctx.send(f'Successfully reloaded extension `cogs.{extension}.`')

def setup(bot):
    bot.add_cog(devCog(bot))
