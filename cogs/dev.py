import discord
from discord.ext import commands
import os
from pydactyl import PterodactylClient
import traceback
import textwrap
import secrets

serverclient = PterodactylClient(secrets.secrets_server_url, secrets.secrets_server_key)
my_servers = serverclient.client.list_servers()
srv_id = my_servers[0]['identifier']

class devCog(commands.Cog):
    """Developer commands"""

    def __init__(self, bot):
        self.bot = bot
        self.db_conn = bot.db_conn
        self.colour = 0xff9300
        self.footer = 'Bot developed by DevilJamJar#0001\nWith a lot of help from ♿nizcomix#7532'
        self.thumb = 'https://styles.redditmedia.com/t5_3el0q/styles/communityIcon_iag4ayvh1eq41.jpg'

    # {'state': 'on', 'memory': {'current': 111, 'limit': 256}, 'cpu': {'current': 1.539, 'cores': [0.397, 0.137, 0.68, 0, 0, 0.155, 0, 0, 0, 0.169], 'limit': 200}, 'disk': {'current': 50, 'limit': 3000}}
    @commands.command(aliases=['ss'])
    @commands.is_owner()
    async def serverstats(self, ctx):
        """Retrieves server information"""
        srv_utilization2 = serverclient.client.get_server_utilization(srv_id)
        await ctx.send(f'**Server Information**\n\
State: `{srv_utilization2["state"]}`\n\
Memory Usage: `{srv_utilization2["memory"]["current"]}MB`\n\
CPU Usage: `{srv_utilization2["cpu"]["current"]}%`\n\
Disk Usage: `{srv_utilization2["disk"]["current"]}MB`')

    @commands.command(aliases=['sss'])
    @commands.is_owner()
    async def sendserversignal(self, ctx, signal):
        """Sends signal to py-dactl server"""
        known = [
            'stop',
            'restart',
            'kill'
        ]
        if signal.lower() in known:
            try:
                await ctx.send('`Trying...`')
                serverclient.client.send_power_action(srv_id, signal)
            except:
                pass

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
                if filename.endswith('.py') and filename != 'dev.py' and filename != 'secrets.py':
                    self.bot.unload_extension(f'cogs.{filename[:-3]}')
                    self.bot.load_extension(f'cogs.{filename[:-3]}')
            return await ctx.send('Successfully reloaded extension `all cogs.`')
        self.bot.unload_extension(f'cogs.{extension}')
        self.bot.load_extension(f'cogs.{extension}')
        return await ctx.send(f'Successfully reloaded extension `cogs.{extension}.`')

    @commands.command(name='eval')
    @commands.is_owner()
    async def _eval(self, ctx, *, code):
        if "import os" in code or "import sys" in code:
            return await ctx.send(f"You Can't Do That!")

        code = code.strip('` ')

        env = {
            'bot': self.bot,
            'BOT': self.bot,
            'client': self.bot,
            'ctx': ctx,
            'message': ctx.message,
            'server': ctx.message.guild,
            'guild': ctx.message.guild,
            'channel': ctx.message.channel,
            'author': ctx.message.author,
            'print': ctx.send
        }
        env.update(globals())

        new_forced_async_code = f'async def code():\n{textwrap.indent(code, "    ")}'

        exec(new_forced_async_code, env)
        code = env['code']
        try:
            await code()
        except:
            await ctx.send(f'```{traceback.format_exc()}```')


def setup(bot):
    bot.add_cog(devCog(bot))
