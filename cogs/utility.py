import discord
from discord.ext import commands, buttons

import wikipedia, asyncio, textwrap, aiohttp, json
import googletrans
from PyDictionary import PyDictionary
from googlesearch import search 

from unit_convert import UnitConvert
dictionary=PyDictionary()

def to_emoji(c):
    base = 0x1f1e6
    return chr(base + c)

class MyPaginator(buttons.Paginator):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class utilityCog(commands.Cog):
    """Utility commands"""

    def __init__(self, bot):
        self.bot = bot
        self.db_conn = bot.db_conn
        self.colour = 0xff9300
        self.footer = 'Bot developed by DevilJamJar#0001\nWith a lot of help from ♿nizcomix#7532'
        self.thumb = 'https://styles.redditmedia.com/t5_3el0q/styles/communityIcon_iag4ayvh1eq41.jpg'

        self.trans = googletrans.Translator()

    @commands.command()
    async def google(self, ctx, *, term:str):
        """google a term"""
        results = []
        def scour(term):
            for j in search(term, tld="com", num=10, stop=10, pause=2): 
                results.append(j)
        async with ctx.typing():
            loop = self.bot.loop
            await loop.run_in_executor(None, scour, term)
            if not len(results):
                return await ctx.send('No results found for specified term.')
            pagey = MyPaginator(title='`Google Search Results`', colour=0xff9300, embed=False, timeout=90, use_defaults=True,
                                entries=[str(r) for r in results], length=1)

        await pagey.start(ctx)
    
    @commands.command()
    async def afk(self, ctx, *, reason:str='None Provided'):
        """Sets or removes an outstanding AFK"""
        with open('afks.json', 'r') as f:
            afks = json.load(f)

        try:
            if afks[str(ctx.author.id)]:
                afks.pop(str(ctx.author.id))
                with open('afks.json', 'w') as f:
                    json.dump(afks, f, indent=4)
                return await ctx.send(f'{ctx.author.mention}, I removed your AFK.')
        except KeyError:
            pass
        
        afks[str(ctx.author.id)] = reason
        await ctx.send(f'{ctx.author.mention}, I successfully marked you as AFK.')
        await asyncio.sleep(1)
        with open('afks.json', 'w') as f:
            json.dump(afks, f, indent=4)

    @commands.command(aliases=['df', 'dictionary'])
    async def dict(self, ctx, *, search):
        """Shows top dictionary result"""
        async with ctx.typing():
            meaning = dictionary.meaning(search)
            if not meaning:
                return await ctx.send('Word not found.')
            iterator = iter(meaning.values())
            firstmeaning = next(iterator)
            wordtype = list(meaning.keys())[0]
            if len(firstmeaning):
                firstmeaning = firstmeaning[0].replace('(', '').capitalize()
        embed=discord.Embed(
            title=f'{search.capitalize()}',
            colour=self.colour,
            description=f'Type: `{wordtype}`\nDefinition:\n```fix\n{firstmeaning}\n```'
        )
        return await ctx.send(embed=embed)

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
    async def translate(self, ctx, to:str='en', *, message: commands.clean_content=None):
        """Translates text"""
        if not message:
            raise commands.BadArgument('Please first provide a code to translate into (e.g en is english) and then a message to translate')
        def trans(message, to):
            try:
                done = self.trans.translate(message, dest=to)
                return done
            except:
                raise commands.BadArgument('Please first provide a valid code to translate into (e.g en is english) and then a message to translate')
        async with ctx.typing():
            loop = self.bot.loop
            ret = await loop.run_in_executor(None, trans, message, to)

            embed = discord.Embed(title='Translator', colour=self.colour)
            src = googletrans.LANGUAGES.get(ret.src, '(auto-detected)').title()
            dest = googletrans.LANGUAGES.get(ret.dest, 'Unknown').title()
            embed.add_field(name=f'From {src}', value=ret.origin, inline=True)
            embed.add_field(name=f'To {dest}', value=ret.text, inline=True)
        await ctx.send(embed=embed)

    @commands.command()
    async def poll(self, ctx, *, question):
        """Creates an interactive poll"""
        messages = [ctx.message]
        answers = []

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel and len(m.content) <= 100

        for i in range(20):
            messages.append(await ctx.send(f'Say poll option or `{ctx.prefix}cancel` to publish poll.'))

            try:
                entry = await self.bot.wait_for('message', check=check, timeout=60.0)
            except asyncio.TimeoutError:
                break

            messages.append(entry)

            if entry.clean_content.startswith(f'{ctx.prefix}cancel'):
                break

            answers.append((to_emoji(i), entry.clean_content))

        try:
            await ctx.channel.delete_messages(messages)
        except:
            pass

        answer = '\n'.join(f'{keycap}: {content}' for keycap, content in answers)
        # actual_poll = await ctx.send(f'**{ctx.author} asks: **{question}\n\n{answer}')
        embed=discord.Embed(title=question, colour=self.colour, description=answer)
        embed.set_author(name=f'{ctx.author.name}#{ctx.author.discriminator}', icon_url=ctx.author.avatar_url)
        actual_poll = await ctx.send(embed=embed)
        for emoji, _ in answers:
            await actual_poll.add_reaction(emoji)

    @commands.command(aliases=['emoteurl', 'urlemote', 'emote_url', 'emoji'])
    async def emote(self, ctx, emote:str=None):
        """Returns URL of given emote"""
        if not emote:
            return await ctx.send('You need to provide an `emote`')
        try:
            c = emote
            d = f'{c}' 
            p = int(d.split(':')[2].split('>')[0])
            g = self.bot.get_emoji(p)
        except:
            raise commands.BadArgument("Unknown emote provided.")
        try:
            final_url = f'{g.url}'
        except:
            raise commands.BadArgument("This emote belongs to a guild I am not a member of.")
        embed = discord.Embed(title='Link:', colour=self.colour, description=f'**{final_url}**')
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(utilityCog(bot))
