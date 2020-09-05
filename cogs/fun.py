import discord
from discord.ext import commands

import asyncio, aiohttp, io
import urllib.parse

class funCog(commands.Cog):
    """Fun commands"""

    def __init__(self, bot):
        self.bot = bot
        self.db_conn = bot.db_conn
        self.colour = 0xff9300
        self.footer = 'Bot developed by DevilJamJar#0001\nWith a lot of help from ♿nizcomix#7532'
        self.thumb = 'https://styles.redditmedia.com/t5_3el0q/styles/communityIcon_iag4ayvh1eq41.jpg'

        self.text_to_morse = {
            'A': '.-',     'B': '-...',   'C': '-.-.',   'D': '-..',    'E': '.',       'F': '..-.',
            'G': '--.',    'H': '....',   'I': '..',     'J': '.---',   'K': '-.-',     'L': '.-..',
            'M': '--',     'N': '-.',     'O': '---',    'P': '.--.',   'Q': '--.-',    'R': '.-.',
            'S': '...',    'T': '-',      'U': '..-',    'V': '...-',   'W': '.--',     'X': '-..-',
            'Y': '-.--',   'Z': '--..',    '0': '-----',  '1': '.----',  '2': '..---',   '3': '...--',
            '4': '....-',  '5': '.....',  '6': '-....',  '7': '--...',  '8': '---..',   '9': '----.',
            '.': '.-.-.-', ',': '--..--', '?': '..--..', "'": '.----.', '!': '-.-.--',  "/": '-..-.',
            '(': '-.--.', ')': '-.--.-', '&': '.-...',  ':': '---...', ';': '-.-.-.',  '=': '-...-',
            '+': '.-.-.',  '-': '-....-', '_': '..--.-', '"': '.-..-.', '$': '...-..-', '@': '.--.-.',
            ' ': ' '
        }
        self.morse_to_text = {value: key for key, value in self.text_to_morse.items()}

    @commands.command(aliases=['yodish'])
    async def yoda(self, ctx, *, text:str):
        """Translates text into yodish"""
        base_url = 'https://api.funtranslations.com/translate/yoda.json?text='
        async with aiohttp.ClientSession() as cs, ctx.typing():
            async with cs.get(base_url + text) as r:
                data = await r.json()
        original = data['contents']['text']
        translated = data['contents']['translated']
        embed = discord.Embed(
            title='Yodish Translator',
            colour = self.colour
        )
        embed.add_field(name='Original', value=original.capitalize(), inline=True)
        embed.add_field(name='Yodish', value=translated, inline=True)
        await ctx.send(embed=embed)

    @commands.command(aliases=['affirmate', 'affirmation', 'motivate', 'motivation'])
    async def quote(self, ctx):
        """Collect a truly motivational quote"""
        url = 'https://www.affirmations.dev'
        async with aiohttp.ClientSession() as cs, ctx.typing():
            async with cs.get(url) as r:
                data = await r.json()
        embed = discord.Embed(
            colour = self.colour,
            title=data["affirmation"]
        )
        await ctx.send(embed=embed)

    @commands.command(aliases=['inspiro', 'inspirobot'])
    async def inspire(self, ctx):
        """Collect a not so inspiring quote"""
        url = 'https://inspirobot.me/api?generate=true'
        async with aiohttp.ClientSession() as cs, ctx.typing():
            async with cs.get(url) as r:
                data = await r.text()
        embed = discord.Embed(
            colour = self.colour
        )
        embed.set_image(url=data)
        await ctx.send(embed=embed)

    @commands.command(aliases=['dex', 'poke', 'pokemon', 'poké', 'pokémon'])
    async def pokedex(self, ctx, *, pokemon:str):
        """Return information about specified Pokemon"""
        pokemon=pokemon.lower()
        base_url = 'https://pokeapi.co/api/v2/pokemon/'
        async with aiohttp.ClientSession() as cs, ctx.typing():
            try:
                async with cs.get(base_url + pokemon) as r:
                    data = await r.json()
            except:
                raise commands.BadArgument('Requested Pokémon not found!')
        pokename = data["name"]
        pokenum = f'#{data["id"]}'
        pokeheight = f'{data["height"]}m'
        pokeweight = f'{data["weight"]/10}kg'
        poketypes=[]
        for i in data['types']:
            poketypes.append(f"• {(i['type']['name'].capitalize())}")
        abilities=[]
        for i in data['abilities']:
            abilities.append(f"• {(i['ability']['name'].capitalize())}")
        pokeimg = data['sprites']['other']['official-artwork']['front_default'] or data['sprites']['front_default']
        pokespecies = data['species']['url']
        async with aiohttp.ClientSession() as cs:
            async with cs.get(pokespecies) as r:
                data = await r.json()
        for i in data['flavor_text_entries']:
            if i['language']['name'] == 'en':
                pokedesc = (i['flavor_text']).replace('\n', ' ').lower().capitalize()
                break
        is_legendary = data['is_legendary']
        is_mythical = data['is_mythical']
        evochain = data['evolution_chain']['url']
        async with aiohttp.ClientSession() as cs:
            async with cs.get(evochain) as r:
                data = await r.json()
        evoline = f'{data["chain"]["species"]["name"].capitalize()}'
        if len(data['chain']['evolves_to']):
            evoline+=f' => {data["chain"]["evolves_to"][0]["species"]["name"].capitalize()}'
            if len(data['chain']['evolves_to'][0]['evolves_to']):
                evoline+=f' => {data["chain"]["evolves_to"][0]["evolves_to"][0]["species"]["name"].capitalize()}'
        embed = discord.Embed(
            title=f'{pokename.capitalize()} {pokenum}',
            colour=self.colour,
            description=f'**{pokedesc.capitalize()}**'
        )
        embed.add_field(name=f'Weight', value=f'{pokeweight}', inline=True)
        embed.add_field(name=f'Height', value=f'{pokeheight}', inline=True)
        embed.add_field(name=f'Type(s)', value="\n".join(poketypes), inline=True)
        embed.add_field(name=f'Abilities', value="\n".join(abilities), inline=True)
        embed.add_field(name=f'Evolution Line', value=f'{evoline}', inline=True)
        embed.add_field(name=f'Legendary', value=is_legendary, inline=True)
        embed.add_field(name=f'Mythical', value=is_mythical, inline=True)
        embed.set_image(url=pokeimg)
        return await ctx.send(embed=embed)

    @commands.command()
    async def fact(self,ctx):
        async with aiohttp.ClientSession() as cs:
            async with cs.get(f"https://uselessfacts.jsph.pl/random.json?language=en") as r:
                data = await r.json()
        await ctx.send(data["text"])

    @commands.command()
    async def morse(self, ctx, *, text: commands.clean_content):
        """
        Converts the given text into morse code.
        """

        morse_text = ' '.join([self.text_to_morse.get(letter.upper(), letter) for letter in str(text).strip()])
        return await ctx.send(f'`{morse_text}`')

    @commands.command()
    async def unmorse(self, ctx, *, morse: commands.clean_content):
        """
        Converts the given morse code into text.
        """

        message = []
        for word in str(morse).strip().split('   '):
            message.append(''.join([self.morse_to_text.get(letter.upper(), letter) for letter in word.split()]))
        message = " ".join(message)

        return await ctx.send(f'`{message}`')

    @commands.command(aliases=['catto'])
    async def cat(self, ctx):
        """Generates an awesome cat image"""
        async with aiohttp.ClientSession() as cs:
            async with cs.get("https://api.thecatapi.com/v1/images/search") as resp:
                if resp.status != 200:
                    return await ctx.send('No cat found :(')
                js = await resp.json()
                await ctx.send(embed=discord.Embed(title='Catto :)', color=self.colour).set_image(url=js[0]['url']))

    @commands.command(aliases=['pupper', 'doggo'])
    async def dog(self, ctx):
        """Generates an awesome image or video of a dog"""
        async with aiohttp.ClientSession() as cs:
            async with cs.get("https://random.dog/woof") as resp:
                if resp.status != 200:
                    return await ctx.send('No dog found :(')

                filename = await resp.text()
                url = f'https://random.dog/{filename}'
                filesize = ctx.guild.filesize_limit if ctx.guild else 8388608
                if filename.endswith(('.mp4', '.webm')):
                    async with ctx.typing():
                        async with cs.get(url) as other:
                            if other.status != 200:
                                return await ctx.send('Could not download dog video :(')

                            if int(other.headers['Content-Length']) >= filesize:
                                return await ctx.send(f'Video was too big to upload... See it here: {url} instead.')

                            fp = io.BytesIO(await other.read())
                            await ctx.send(file=discord.File(fp, filename=filename))
                else:
                    await ctx.send(embed=discord.Embed(title='Doggo :)', color=self.colour).set_image(url=url))

def setup(bot):
    bot.add_cog(funCog(bot))
