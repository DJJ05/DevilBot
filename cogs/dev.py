import discord
from discord.ext import commands
import os, json, typing
import traceback
import textwrap
import secrets

class devCog(commands.Cog):
    """Developer commands"""

    def __init__(self, bot):
        self.bot = bot
        self.db_conn = bot.db_conn
        self.colour = 0xff9300
        self.footer = 'Bot developed by DevilJamJar#0001\nWith a lot of help from ♿nizcomix#7532'
        self.thumb = 'https://styles.redditmedia.com/t5_3el0q/styles/communityIcon_iag4ayvh1eq41.jpg'
        
    #async def cog_check(self, ctx):
        #return ctx.author.id == 670564722218762240 # check for all commands in this cog

    @commands.group(invoke_without_command=True, aliases=['err'])
    async def error(self, ctx):
        """Error commands"""
        pass

    @error.command(aliases=['res', 'close'])
    async def resolve(self, ctx, id=None, *, message):
        """Resolve an error"""
        if not id:
            return await ctx.send('ID is a required argument.')
        try:
            id = int(id)
        except:
            return await ctx.send('ID must be a number.')
        if not message:
            return await ctx.send('Message is a required argument.')

        with open('errors.json', 'r') as f:
            errors = json.load(f)

        to_dm = errors[str(id)]['followers']
        if len(to_dm):
            embed=discord.Embed(
                title=f'Error `{id}` has been resolved',
                colour=self.colour,
                description=f"Command: `{errors[str(id)]['command']}`\nClosure reason: `{message.capitalize()}`\nOriginal traceback: {errors[str(id)]['traceback']}"
            )
            for user in to_dm:
                a = self.bot.get_user(int(user))
                try:
                    await a.send(embed=embed)
                except:
                    await ctx.send(f'Attempt to DM `<@!{user}>` failed.')

        errchannel = self.bot.get_channel(748962623487344753)
        await errchannel.send(f'**ERROR {id} HAS BEEN RESOLVED.**')
        errors.pop(str(id))
        return await ctx.send('Done.')

    @error.command(aliases=['bc'])
    async def broadcast(self, ctx, id=None, *, message):
        """Broadcast an error update"""
        if not id:
            return await ctx.send('ID is a required argument.')
        try:
            id = int(id)
        except:
            return await ctx.send('ID must be a number.')
        if not message:
            return await ctx.send('Message is a required argument.')

        with open('errors.json', 'r') as f:
            errors = json.load(f)

        to_dm = errors[str(id)]['followers']
        if not len(to_dm):
            try:
                await ctx.message.delete()
            except:
                pass
            return await ctx.send(f'Error `{id}` has no active followers.')
        embed=discord.Embed(
            title=f'New comment on error `{id}`',
            colour=self.colour,
            description=f"Command: `{errors[str(id)]['command']}`\nNew comment: `{message.capitalize()}`\nOriginal traceback: {errors[str(id)]['traceback']}"
        )
        for user in to_dm:
            a = self.bot.get_user(int(user))
            try:
                await a.send(embed=embed)
            except:
                await ctx.send(f'Attempt to DM `<@!{user}>` failed.')
        await ctx.send('Done.')

    @error.command()
    async def follow(self, ctx, id=None):
        """Follow an error"""
        if not id:
            return await ctx.send('ID is a required argument.')
        try:
            id = int(id)
        except:
            return await ctx.send('ID must be a number.')

        with open('errors.json', 'r') as f:
            errors = json.load(f)

        try:
            if str(ctx.author.id) in errors[str(id)]["followers"]:
                return await ctx.send('You have already followed this error!')
            errors[str(id)]["followers"].append(str(ctx.author.id))
        except KeyError:
            return await ctx.send('Invalid ID. Please check for typos.')

        with open('errors.json', 'w') as f:
            json.dump(errors, f, indent=4)

        return await ctx.send(f'Successfully followed `{id}.` You can use `{ctx.prefix}error unfollow {id}` at anytime to unfollow this error.')

    @error.command()
    async def unfollow(self, ctx, id=None):
        """Unfollow an error"""
        if not id:
            return await ctx.send('ID is a required argument.')
        try:
            id = int(id)
        except:
            return await ctx.send('ID must be a number.')

        with open('errors.json', 'r') as f:
            errors = json.load(f)

        try:
            if str(ctx.author.id) in errors[str(id)]["followers"]:
                errors[str(id)]["followers"].remove(str(ctx.author.id))
            else:
                return await ctx.send('You are not following this error!')
        except KeyError:
            return await ctx.send('Invalid ID. Please check for typos.')

        with open('errors.json', 'w') as f:
            json.dump(errors, f, indent=4)

        return await ctx.send(f'Successfully unfollowed `{id}.` You can use `{ctx.prefix}error follow {id}` at anytime to follow this error.')

    @commands.group(invoke_without_command=True, aliases=['bl'])
    async def blacklist(self, ctx):
        """Blacklisting commands"""
        pass
    
    @blacklist.command(aliases=['addmember'])
    @commands.is_owner()
    async def adduser(self, ctx, member:typing.Union[discord.Member, int], *, reason:str='None Provided'):
        if not member:
            return await ctx.send('`Member` is a required argument that is missing.') # ???
        if type(member) == int:
            member = self.bot.get_user(member) or await self.bot.fetch_user(member)
        with open('blacklist.json', 'r') as f:
            blacklist = json.load(f)

        blacklist['users'][str(member.id)] = reason.capitalize()
        self.bot.blacklist['users'][str(member.id)] = reason.capitalize()

        with open('blacklist.json', 'w') as f:
            json.dump(blacklist, f, indent=4)
        
        await ctx.send('Done.')

        try:
            embed = discord.Embed(title=f'You have been blacklisted from utilising my commands.', colour=self.colour,
                                  description=f'Reason: `{reason.capitalize()}`')
            await member.send(embed=embed)
            await ctx.send('DM sent successfully.')
        except:
            await ctx.send('DM failed to send.')
    
    @blacklist.command(aliases=['remmember'])
    @commands.is_owner()
    async def remuser(self, ctx, member:typing.Union[discord.Member, int]):
        if not member:
            return await ctx.send('`Member` is a required argument that is missing.')
        if type(member) == int:
            member = self.bot.get_user(member) or await self.bot.fetch_user(member)
        with open('blacklist.json', 'r') as f:
            blacklist = json.load(f)

        try:
            self.bot.blacklist['users'].pop(str(member.id))
            blacklist['users'].pop(str(member.id))
        except:
            return await ctx.send('`Member` not found in blacklist.')

        with open('blacklist.json', 'w') as f:
            json.dump(blacklist, f, indent=4)

        await ctx.send('Done.')

        try:
            embed = discord.Embed(title=f'You have been unblacklisted from utilising my commands.', colour=self.colour)
            await member.send(embed=embed)
            await ctx.send('DM sent successfully.')
        except:
            await ctx.send('DM failed to send.')

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
            'print': ctx.send # ah yes, await print()
        }
        env.update(globals())

        new_forced_async_code = f'async def code():\n{textwrap.indent(code, "    ")}'

        exec(new_forced_async_code, env)
        code = env['code']
        try:
            await code()
        except:
            await ctx.send(f'```{traceback.format_exc()}```')

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

def setup(bot):
    bot.add_cog(devCog(bot))
