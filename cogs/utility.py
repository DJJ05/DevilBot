import discord
from discord.ext import commands, buttons

import wikipedia, asyncio, textwrap, aiohttp, json
import googletrans
from PyDictionary import PyDictionary
from googlesearch import search 

from unit_convert import UnitConvert
from discord.ext.commands.cooldowns import BucketType
import unicodedata
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

    '''
    Copyright (c) 2020 Rapptz
    https://github.com/Rapptz/RoboDanny/blob/rewrite/cogs/meta.py#L223-L237
    under the terms of the  MIT LICENSE
    '''

    @commands.command(aliases=['embedder'])
    @commands.max_concurrency(1, BucketType.channel)
    async def embed(self, ctx):
        """Sends a COPYABLE embed in the channel for you to use anywhere you like"""
        displayable = 'https://embed.rauf.wtf/'
        def check(m):
            return m.channel.id == ctx.channel.id and m.author.id == ctx.author.id
        try:
            a = await ctx.send('Alright, send me the embed title text. Note: this is a required argument.')
            msg = await self.bot.wait_for('message', check=check,timeout=30)
        except asyncio.TimeoutError:
            return await ctx.send("You didn't reply in 30 seconds, so the request timed out.")
        else:
            displayable += f"{msg.content.replace(' ', '+')}?"
            try:
                await msg.delete()
                await a.delete()
            except discord.Forbidden:
                pass
        b = await ctx.send('Alright, recorded your embed title. Next, send me the author of the embed. Say "None" to leave this field blank.')

        try:
            msg = await self.bot.wait_for('message', check=check,timeout=30)
        except asyncio.TimeoutError:
            return await ctx.send("You didn't reply in 30 seconds, so the request timed out.")
        else:
            if not msg.content.lower() == 'none':
                displayable += f"&author={msg.content.replace(' ', '+')}"
            try:
                await msg.delete()
                await b.delete()
            except discord.Forbidden:
                pass
        c = await ctx.send('Alright, next I need the colour of your embed in hex form. This will default to black. Say "None" to leave this field blank.')

        try:
            msg = await self.bot.wait_for('message', check=check,timeout=30)
        except asyncio.TimeoutError:
            return await ctx.send("You didn't reply in 30 seconds, so the request timed out.")
        else:
            if not msg.content.lower() == 'none':
                displayable += f"&color={msg.content.replace(' ', '+').replace('#', '')}"
            try:
                await msg.delete()
                await c.delete()
            except discord.Forbidden:
                pass
        d = await ctx.send('Alright, next I need the image URL of the embed that will be displayed below the title. Say "None" to leave this field blank.')

        try:
            msg = await self.bot.wait_for('message', check=check,timeout=30)
        except asyncio.TimeoutError:
            return await ctx.send("You didn't reply in 30 seconds, so the request timed out.")
        else:
            if not msg.content.lower() == 'none':
                displayable += f"&image={msg.content.replace(' ', '+')}"
            try:
                await msg.delete()
                await d.delete()
            except discord.Forbidden:
                pass
        e = await ctx.send('Alright, finally I need the redirect URL of the embed, the website users will go to when they click the link. Say "None" to leave this field blank.')

        try:
            msg = await self.bot.wait_for('message', check=check,timeout=30)
        except asyncio.TimeoutError:
            return await ctx.send("You didn't reply in 30 seconds, so the request timed out.")
        else:
            if not msg.content.lower() == 'none':
                displayable += f"&url={msg.content.replace(' ', '+')}"
            try:
                await msg.delete()
                await e.delete()
            except discord.Forbidden:
                pass
            await ctx.send(f'Alright, I have all I need. To send this embed anywhere, copy this link and paste it wherever you want.\n\n```fix\n{displayable}\n```\n\nHere is a visual representation of your embed:')
        return await ctx.send(displayable)

    @commands.command()
    async def charinfo(self, ctx, *, characters: str):
        """Shows you information about a number of characters."""
        def to_string(c):
            digit = f'{ord(c):x}'
            name = unicodedata.name(c, 'Name not found.')
            return f'`\\U{digit:>08}`: {name} - {c} \N{EM DASH} <http://www.fileformat.info/info/unicode/char/{digit}>'
        msg = '\n'.join(map(to_string, characters))
        if len(msg) > 2000:
            return await ctx.send('Output too long to display.')
        await ctx.send(msg)

    @commands.command(aliases=['rtfd'])
    async def rtfm(self, ctx, *, search):
        """Read the fucking manual"""

    @commands.command()
    async def rtfs(self, ctx, *, search):
        """Read the fucking source"""
        base_url = 'https://rtfs.eviee.me/dpy?search='
        async with aiohttp.ClientSession() as cs, ctx.typing():
            async with cs.get(base_url + search) as r:
                data = await r.json()
        if not data:
            raise commands.BadArgument('Not found')
        final = []
        skip = []
        for i in data:
            if not i['url'] in skip:
                if i['parent']:
                    pathname = f'{i["parent"]}.{i["object"]}'
                else:
                    pathname = f'{i["object"]}'
                final.append(f'`{pathname}`\n{i["url"]}')
                skip.append(i['url'])
        pagey = MyPaginator(colour=0xff9300, embed=True, timeout=180, use_defaults=True,
                                entries=[i for i in final], length=5)
        await pagey.start(ctx)

    @commands.command(aliases=['iplookup', 'ipsearch'])
    @commands.cooldown(1,180,BucketType.user)
    async def whois(self, ctx, IP:str):
        """IPLookup and analysis tool"""
        IP = f'{IP}?lang=en'
        base_url = 'http://ipwhois.app/json/'
        async with aiohttp.ClientSession() as cs, ctx.typing():
            async with cs.get(base_url + IP) as r:
                data = await r.json()
        if not data['success']:
            embed=discord.Embed(
                title=f'IP: {IP.capitalize()}',
                colour=self.colour,
                description=f"Success: `{data['success']}`\nReason: `{data['message'].capitalize()}`"
            )
            return await ctx.send(embed=embed)
        embed=discord.Embed(
            colour=self.colour,
            title=f'IP Address: {data["ip"]}'
        )
        embed.add_field(name='Type:', value=data['type'] or 'None', inline=True)
        embed.add_field(name='Continent:', value=data['continent'] or 'None', inline=True)
        embed.add_field(name='Continent Code:', value=data['continent_code'] or 'None', inline=True)
        embed.add_field(name='Country:', value=data['country'] or 'None', inline=True)
        embed.add_field(name='Country Code:', value=data['country_code'] or 'None', inline=True)
        embed.add_field(name='Country Capital:', value=data['country_capital'] or 'None', inline=True)
        embed.add_field(name='Country Phone:', value=data['country_phone'] or 'None', inline=True)
        embed.add_field(name='Region:', value=data['region'] or 'None', inline=True)
        embed.add_field(name='City:', value=data['city'] or 'None', inline=True)
        embed.add_field(name='Latitude:', value=data['latitude'] or 'None', inline=True)
        embed.add_field(name='Longitude:', value=data['longitude'] or 'None', inline=True)
        embed.add_field(name='ASN:', value=data['asn'] or 'None', inline=True)
        embed.add_field(name='ORG:', value=data['org'] or 'None', inline=True)
        embed.add_field(name='ISP:', value=data['isp'] or 'None', inline=True)
        embed.add_field(name='Timezone:', value=data['timezone'] or 'None', inline=True)
        embed.add_field(name='Timezone Name:', value=data['timezone_name'] or 'None', inline=True)
        embed.add_field(name='Timezone GMT:', value=data['timezone_gmtOffset'] or 'None', inline=True)
        embed.add_field(name='Currency:', value=data['currency'] or 'None', inline=True)
        embed.add_field(name='Currency Code:', value=data['currency_code'] or 'None', inline=True)
        embed.set_image(url=data['country_flag'])
        await ctx.send(embed=embed)

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
        
        finaltime = str(ctx.message.created_at).split(' ')[1].replace(':', '').replace('.', '')
        afks[str(ctx.author.id)] = {"message":reason, "time": finaltime}
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
        def scour(search):
            return wikipedia.search(search)
        async with ctx.typing():
            loop = self.bot.loop
            results = await loop.run_in_executor(None, scour, search)
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
