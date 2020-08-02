import discord
from discord.ext import commands

import wikipedia, asyncio, textwrap, aiohttp
import googletrans

class utilityCog(commands.Cog):
    """Utility commands"""

    def __init__(self, bot):
        self.bot = bot
        self.db_conn = bot.db_conn
        self.colour = 0xff9300
        self.footer = 'Bot developed by DevilJamJar#0001\nWith a lot of help from ♿nizcomix#7532'
        self.thumb = 'https://styles.redditmedia.com/t5_3el0q/styles/communityIcon_iag4ayvh1eq41.jpg'

        self.trans = googletrans.Translator()

    @commands.command(aliases=['wiki'])
    async def wikipedia(self, ctx, *, search: str = None):
        """Shows top wikipedia result"""
        if not search:
            return await ctx.send('`Search` is a required argument that is missing.')
        async with ctx.typing():
            results = wikipedia.search(search)
            if not len(results):
                await ctx.channel.send("Sorry, I didn't find any results.")
                await asyncio.sleep(5)
                return

            newSearch = results[0]

            wik = wikipedia.page(newSearch)

            embed = discord.Embed(title=wik.title, colour=self.colour, url=wik.url)
            textList = textwrap.wrap(wik.content, 500, break_long_words=True, replace_whitespace=False)
            embed.add_field(name="Wikipedia Results", value=textList[0] + "...")
        await ctx.send(embed=embed)

    @commands.command()
    async def tinyurl(self, ctx, *, link: str):
        """shrinks a link using tinyurl"""
        url = link.strip("<>")
        url = 'http://tinyurl.com/api-create.php?url=' + url
        async with aiohttp.ClientSession() as cs:
            async with cs.get(url) as resp:
                new = await resp.text()
        embed = discord.Embed(title='TinyURL Link Shortener', color=self.colour)
        embed.add_field(name='Original Link', value=link, inline=False)
        embed.add_field(name='Shortened Link', value=new, inline=False)
        await ctx.send(embed=embed)
        try:
            await ctx.message.delete()
        except discord.errors.Forbidden:
            pass

    @commands.command(aliases=['invinfo', 'inviteinfo', 'fetchinvite'])
    async def fetchinv(self, ctx, *, inv: str = None):
        '''Provides limited information about any invite link.'''
        if inv == None:
            return await ctx.send('Missing argument: `inv.` Please provide an `invite link` or `invite code.`')
        if 'discord.gg/' in inv:
            fetched_inv = await self.bot.fetch_invite(f'{inv}')
        else:
            fetched_inv = await self.bot.fetch_invite(f'discord.gg/{inv}')
            inv_description = fetched_inv.guild.description if fetched_inv.guild.description else None
            features_list = '\n'.join([f.lower().title().replace('_', ' ') for f in fetched_inv.guild.features]) if fetched_inv.guild.features else None
            embed = discord.Embed(title=f"Resolved Invite: {fetched_inv.code}", colour=0xff9300)
            embed.add_field(name='**General:**',
                            value=
                                f'Name: **{fetched_inv.guild.name}**\n'
                                f'Description: **{inv_description}**\n'
                                f'<:member:716339965771907099> **{fetched_inv.approximate_member_count}**\n'
                                f'<:online:726127263401246832> **{fetched_inv.approximate_presence_count}**\n')
            embed.add_field(name='**Features:**',
                            value=features_list)

            embed.set_footer(text=f'Guild ID: {fetched_inv.guild.id}  |  Requested by: {ctx.author.name}#{ctx.author.discriminator}')
            await ctx.send(embed=embed)

    @commands.command()
    async def hastebin(self, ctx, *, code):
        """Hastebin-ify some code"""
        if code.startswith('```') and code.endswith('```'):
            code = code[3:-3]
        else:
            code = code.strip('` \n')
        async with aiohttp.ClientSession() as cs:
            async with cs.post("https://hastebin.com/documents", data=code) as resp:
                data = await resp.json()
                key = data['key']
        embed = discord.Embed(color=self.colour, title='Hastebin-ified Code:', description=f"https://hastebin.com/{key}") 
        await ctx.send(embed=embed)

    @commands.command(aliases=['trans'])
    async def translate(self, ctx, *, message: commands.clean_content):
        """Auto Detects and translates text into English"""
        loop = self.bot.loop

        ret = await loop.run_in_executor(None, self.trans.translate, message)

        embed = discord.Embed(title='Auto-Detection Translator', colour=self.colour)
        src = googletrans.LANGUAGES.get(ret.src, '(auto-detected)').title()
        dest = googletrans.LANGUAGES.get(ret.dest, 'Unknown').title()
        embed.add_field(name=f'From {src}', value=ret.origin, inline=True)
        embed.add_field(name=f'To {dest}', value=ret.text, inline=True)
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(utilityCog(bot))
