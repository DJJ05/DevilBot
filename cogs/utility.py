import asyncio
import json
import re
import textwrap
import unicodedata

import aiohttp
import googletrans
import cv2
import discord
import pytesseract
import wikipedia
from PIL import Image
from PyDictionary import PyDictionary
from discord.ext import commands, buttons
from discord.ext.commands.cooldowns import BucketType
from googlesearch import search
from .secrets import *

dictionary = PyDictionary()


def to_emoji(c):
    base = 0x1f1e6
    return chr(base + c)


def imgtess(filename: str, blur=None):
    image = cv2.imread(filename)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    if blur:
        gray = cv2.medianBlur(gray, blur)

    filename = "DevilBotOCRFinal.png"
    cv2.imwrite(filename, gray)

    text = pytesseract.image_to_string(Image.open(filename))
    return text


class MyPaginator(buttons.Paginator):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


time_regex = re.compile("(?:(\d{1,5})(h|s|m|d))+?")
time_dict = {"h": 3600, "s": 1, "m": 60, "d": 86400}


class TimeConverter(commands.Converter):
    async def convert(self, ctx, argument):
        args = argument.lower()
        matches = re.findall(time_regex, args)
        time = 0
        for v, k in matches:
            try:
                time += time_dict[k] * float(v)
            except KeyError:
                raise commands.BadArgument(f"{k} is an invalid time-key! h/m/s/d are valid!")
            except ValueError:
                raise commands.BadArgument(f"{v} is not a number!")
        return [argument, time]


class utilityCog(commands.Cog):
    """Utility commands"""

    def __init__(self, bot):
        self.bot = bot
        self.colour = 0xff9300
        self.footer = 'Bot developed by DevilJamJar#0001\nWith a lot of help from ♿nizcomix#7532'
        self.thumb = 'https://styles.redditmedia.com/t5_3el0q/styles/communityIcon_iag4ayvh1eq41.jpg'
        self.trans = googletrans.Translator()

    @commands.command(aliases=['remindme', 'reminder', 'timer'])
    async def remind(self, ctx, time: TimeConverter, *, event='None Provided'):
        """Reminds you about something. Example usage: `remind 2h vote DevilBot`"""
        await ctx.send(f'Alright, I\'ll remind you in `{time[0]}` because: **{event}**.')
        await asyncio.sleep(time[1])
        await ctx.send(f'{ctx.author.mention}, reminder from `{time[0]}` ago: **{event}**.')

    @commands.command(aliases=['ocr', 'itt'])
    async def imagetotext(self, ctx, blur: int, url: str = None):
        """Converts a given image into copy-pastable text using specified blur to hide noise. EMPTY PNG's ARE BUGGY!"""
        if not url:
            if len(ctx.message.attachments) == 0:
                return await ctx.send('I need a valid image attachment to work with!')

            i = ctx.message.attachments[0]
            await i.save('DevilBotOCR.png')

        else:
            async with aiohttp.ClientSession() as cs:
                async with cs.get(url) as res:
                    data = await res.read()

            if res.status != 200:
                return await ctx.send('Connection to URL was not OK\'d, make sure its a valid image.')

            with open('DevilBotOCR.png', 'wb') as file:
                file.write(data)

        await ctx.trigger_typing()

        if blur % 2 == 0:
            blur += 1

        try:
            loop = self.bot.loop
            t = await loop.run_in_executor(None, imgtess, 'DevilBotOCR.png', blur)
        except Exception:
            return await ctx.send('Not a valid image file, weird sizing or another imaging issue occured.')

        e = discord.Embed(
            description=f'```fix\n\u200b{t}\n```',
            colour=self.colour
        )
        return await ctx.send(embed=e)

    @commands.command(aliases=['embedder'])
    @commands.max_concurrency(1, BucketType.channel)
    async def embed(self, ctx):
        """Sends a COPYABLE embed in the channel for you to use anywhere you like"""
        displayable = 'https://embed.rauf.wtf/'

        def check(m):
            return m.channel.id == ctx.channel.id and m.author.id == ctx.author.id

        try:
            a = await ctx.send(
                'Alright, send me the embed title text. Note: this is a required argument. PS: Try avoiding using characters other than a-Z and 0-9 since this can cause errors.')
            msg = await self.bot.wait_for('message', check=check, timeout=30)
        except asyncio.TimeoutError:
            return await ctx.send("You didn't reply in 30 seconds, so the request timed out.")
        else:
            displayable += f"{msg.content.replace(' ', '+')}?"
            try:
                await msg.delete()
                await a.delete()
            except discord.Forbidden:
                pass
        b = await ctx.send(
            'Alright, recorded your embed title. Next, send me the author of the embed. Say "None" to leave this field blank. PS: Try avoiding using characters other than a-Z and 0-9 since this can cause errors.')

        try:
            msg = await self.bot.wait_for('message', check=check, timeout=30)
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
        c = await ctx.send(
            'Alright, next I need the colour of your embed in hex form. This will default to black. Say "None" to leave this field blank.')

        try:
            msg = await self.bot.wait_for('message', check=check, timeout=30)
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
        d = await ctx.send(
            'Alright, next I need the image URL of the embed that will be displayed below the title. Say "None" to leave this field blank.')

        try:
            msg = await self.bot.wait_for('message', check=check, timeout=30)
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
        e = await ctx.send(
            'Alright, finally I need the redirect URL of the embed, the website users will go to when they click the link. Say "None" to leave this field blank.')

        try:
            msg = await self.bot.wait_for('message', check=check, timeout=30)
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
            await ctx.send(
                f'Alright, I have all I need. To send this embed anywhere, copy this link and paste it wherever you want.\n\n```fix\n{displayable}\n```\n\nHere is a visual representation of your embed:')
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

    @commands.command(aliases=['iplookup', 'ipsearch'])
    @commands.cooldown(1, 180, BucketType.user)
    async def whois(self, ctx, IP: str):
        """IPLookup and analysis tool"""
        IP = f'{IP}?lang=en'
        base_url = 'http://ipwhois.app/json/'
        async with aiohttp.ClientSession() as cs, ctx.typing():
            async with cs.get(base_url + IP) as r:
                data = await r.json()
        if not data['success']:
            embed = discord.Embed(
                title=f'IP: {IP.capitalize()}',
                colour=self.colour,
                description=f"Success: `{data['success']}`\nReason: `{data['message'].capitalize()}`"
            )
            return await ctx.send(embed=embed)
        embed = discord.Embed(
            colour=self.colour,
            title=f'IP Address: {data["ip"]}'
        )
        embed.add_field(
            name='Type:', value=data['type'] or 'None', inline=True)
        embed.add_field(name='Continent:',
                        value=data['continent'] or 'None', inline=True)
        embed.add_field(name='Continent Code:',
                        value=data['continent_code'] or 'None', inline=True)
        embed.add_field(name='Country:',
                        value=data['country'] or 'None', inline=True)
        embed.add_field(name='Country Code:',
                        value=data['country_code'] or 'None', inline=True)
        embed.add_field(name='Country Capital:',
                        value=data['country_capital'] or 'None', inline=True)
        embed.add_field(name='Country Phone:',
                        value=data['country_phone'] or 'None', inline=True)
        embed.add_field(
            name='Region:', value=data['region'] or 'None', inline=True)
        embed.add_field(
            name='City:', value=data['city'] or 'None', inline=True)
        embed.add_field(name='Latitude:',
                        value=data['latitude'] or 'None', inline=True)
        embed.add_field(name='Longitude:',
                        value=data['longitude'] or 'None', inline=True)
        embed.add_field(name='ASN:', value=data['asn'] or 'None', inline=True)
        embed.add_field(name='ORG:', value=data['org'] or 'None', inline=True)
        embed.add_field(name='ISP:', value=data['isp'] or 'None', inline=True)
        embed.add_field(name='Timezone:',
                        value=data['timezone'] or 'None', inline=True)
        embed.add_field(name='Timezone Name:',
                        value=data['timezone_name'] or 'None', inline=True)
        embed.add_field(name='Timezone GMT:',
                        value=data['timezone_gmtOffset'] or 'None', inline=True)
        embed.add_field(name='Currency:',
                        value=data['currency'] or 'None', inline=True)
        embed.add_field(name='Currency Code:',
                        value=data['currency_code'] or 'None', inline=True)
        embed.set_image(url=data['country_flag'])
        await ctx.send(embed=embed)

    @commands.command()
    async def afk(self, ctx, *, reason: str = 'None Provided'):
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

        finaltime = str(ctx.message.created_at).split(
            ' ')[1].replace(':', '').replace('.', '')
        afks[str(ctx.author.id)] = {"message": reason, "time": finaltime}
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
        embed = discord.Embed(
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

            embed = discord.Embed(
                title=wik.title, colour=self.colour, url=wik.url)
            textList = textwrap.wrap(
                wik.content, 500, break_long_words=True, replace_whitespace=False)
            embed.add_field(name="Wikipedia Results",
                            value=textList[0] + "...")
        await ctx.send(embed=embed)

    @commands.command()
    async def tinyurl(self, ctx, *, link: str):
        """shrinks a link using tinyurl"""
        url = link.strip("<>")
        url = 'http://tinyurl.com/api-create.php?url=' + url
        async with aiohttp.ClientSession() as cs:
            async with cs.get(url) as resp:
                new = await resp.text()
        embed = discord.Embed(
            title='TinyURL Link Shortener', color=self.colour)
        embed.add_field(name='Original Link', value=link, inline=False)
        embed.add_field(name='Shortened Link', value=new, inline=False)
        await ctx.send(embed=embed)
        try:
            await ctx.message.delete()
        except discord.errors.Forbidden:
            pass

    @commands.command(aliases=['imdb', 'movieinfo', 'tvinfo', 'tv', 'tvshow'])
    async def movie(self, ctx, *, moviename: str):
        """Fetch movie information from IMDB"""
        async with aiohttp.ClientSession() as cs, ctx.typing():
            async with cs.get(
                    f'http://www.omdbapi.com/?apikey={secrets_moviedb}&t={moviename.lower().title().replace(" ", "+")}') as resp:
                data = await resp.json()

        if data['Response'] == 'False':
            raise commands.BadArgument('Invalid movie title provided, no results found.')

        embed = discord.Embed(
            colour=self.colour,
            title=f"__{data['Title']}__",
            description=f'**Plot Line:**\n||{data["Plot"]}||'
        )

        prod = 'N/A'
        try:
            prod = data['Production']
        except:
            ...

        embed.add_field(name='Released', value=data['Released'])
        embed.add_field(name='Rated', value=data['Rated'])
        embed.add_field(name='Runtime', value=data['Runtime'])
        embed.add_field(name='Genre(s)', value=data['Genre'])
        embed.add_field(name='Director', value=data['Director'])
        embed.add_field(name='Writer(s)', value=data['Writer'])
        embed.add_field(name='Language(s)', value=data['Language'])
        embed.add_field(name='Awards', value=data['Awards'])
        embed.add_field(name='IMDB Rating', value=f"{data['imdbRating']}/10")
        embed.add_field(name='IMDB Votes', value=data['imdbVotes'])
        embed.add_field(name='IMDB ID', value=data['imdbID'])
        embed.add_field(name='Production', value=prod)
        embed.set_thumbnail(url=data['Poster'])

        try:
            return await ctx.send(embed=embed)
        except:
            embed.set_thumbnail(
                url='https://m.media-amazon.com/images/G/01/imdb/images/social/imdb_logo._CB410901634_.png')
            return await ctx.send(embed=embed)

    @commands.command(aliases=['invinfo', 'inviteinfo', 'fetchinvite'])
    async def fetchinv(self, ctx, *, inv: str = None):
        """Provides limited information about any invite link."""
        if inv == None:
            return await ctx.send('Missing argument: `inv.` Please provide an `invite link` or `invite code.`')
        if 'discord.gg/' in inv:
            fetched_inv = await self.bot.fetch_invite(f'{inv}')
        else:
            fetched_inv = await self.bot.fetch_invite(f'discord.gg/{inv}')
            inv_description = fetched_inv.guild.description if fetched_inv.guild.description else None
            features_list = '\n'.join([f.lower().title().replace(
                '_', ' ') for f in fetched_inv.guild.features]) if fetched_inv.guild.features else None
            embed = discord.Embed(
                title=f"Resolved Invite: {fetched_inv.code}", colour=0xff9300)
            embed.add_field(name='**General:**',
                            value=f'Name: **{fetched_inv.guild.name}**\n'
                                  f'Description: **{inv_description}**\n'
                                  f'<:member:716339965771907099> **{fetched_inv.approximate_member_count}**\n'
                                  f'<:online:726127263401246832> **{fetched_inv.approximate_presence_count}**\n')
            embed.add_field(name='**Features:**',
                            value=features_list)

            embed.set_footer(
                text=f'Guild ID: {fetched_inv.guild.id}  |  Requested by: {ctx.author.name}#{ctx.author.discriminator}')
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
        embed = discord.Embed(color=self.colour, title='Hastebin-ified Code:',
                              description=f"https://hastebin.com/{key}")
        await ctx.send(embed=embed)

    @commands.command(aliases=['trans'])
    async def translate(self, ctx, to, *, message: commands.clean_content):
        """Translates text"""
        return await ctx.send('The googletrans API is broken atm, its not my fault sorry.')
        result = await self.bot.loop.run_in_executor(None, self.trans.translate, message, to)
        await ctx.send(result)

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

        answer = '\n'.join(
            f'{keycap}: {content}' for keycap, content in answers)
        # actual_poll = await ctx.send(f'**{ctx.author} asks: **{question}\n\n{answer}')
        embed = discord.Embed(
            title=question, colour=self.colour, description=answer)
        embed.set_author(
            name=f'{ctx.author.name}#{ctx.author.discriminator}', icon_url=ctx.author.avatar_url)
        actual_poll = await ctx.send(embed=embed)
        for emoji, _ in answers:
            await actual_poll.add_reaction(emoji)

    @commands.command(aliases=['emoteurl', 'urlemote', 'emote_url', 'emoji'])
    async def emote(self, ctx, emote: str = None):
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
            raise commands.BadArgument(
                "This emote belongs to a guild I am not a member of.")
        embed = discord.Embed(
            title='Link:', colour=self.colour, description=f'**{final_url}**')
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(utilityCog(bot))
