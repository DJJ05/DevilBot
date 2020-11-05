import io
import random
import string

import aiohttp
import discord
from captcha.image import ImageCaptcha
from discord.ext import commands


class funCog(commands.Cog):
    """Fun commands"""

    def __init__(self, bot):
        self.bot = bot
        self.db_conn = bot.db_conn
        self.colour = 0xff9300
        self.footer = 'Bot developed by DevilJamJar#0001\nWith a lot of help from ♿nizcomix#7532'
        self.thumb = 'https://styles.redditmedia.com/t5_3el0q/styles/communityIcon_iag4ayvh1eq41.jpg'
        self.image = ImageCaptcha()

        self.text_to_morse = {
            'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.',
            'G': '--.', 'H': '....', 'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..',
            'M': '--', 'N': '-.', 'O': '---', 'P': '.--.', 'Q': '--.-', 'R': '.-.',
            'S': '...', 'T': '-', 'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-',
            'Y': '-.--', 'Z': '--..', '0': '-----', '1': '.----', '2': '..---', '3': '...--',
            '4': '....-', '5': '.....', '6': '-....', '7': '--...', '8': '---..', '9': '----.',
            '.': '.-.-.-', ',': '--..--', '?': '..--..', "'": '.----.', '!': '-.-.--', "/": '-..-.',
            '(': '-.--.', ')': '-.--.-', '&': '.-...', ':': '---...', ';': '-.-.-.', '=': '-...-',
            '+': '.-.-.', '-': '-....-', '_': '..--.-', '"': '.-..-.', '$': '...-..-', '@': '.--.-.',
            ' ': ' '
        }
        self.morse_to_text = {value: key for key,
                                             value in self.text_to_morse.items()}

    @commands.command()
    async def captcha(self, ctx, *, characters: str = None):
        """Generate a random image captcha with given characters or a random 6 digit one"""
        if not characters:
            characters = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        self.image.write(characters, 'captcha.png')
        f = discord.File('captcha.png')
        return await ctx.send(file=f)

    @commands.command(aliases=['tronalddump', 'tronald', 'donaldtrump', 'trump'])
    async def donald(self, ctx):
        """Collect a random stupid quote from Donald Trump"""
        url = 'https://www.tronalddump.io/random/quote'
        async with aiohttp.ClientSession() as cs, ctx.typing():
            async with cs.get(url) as r:
                data = await r.json()
        await ctx.send(f'**Donald Trump:** {data["value"].capitalize()}')

    @commands.command(aliases=['yodish'])
    async def yoda(self, ctx, *, text: str):
        """Translates text into yodish"""
        base_url = 'https://api.funtranslations.com/translate/yoda.json?text='
        async with aiohttp.ClientSession() as cs, ctx.typing():
            async with cs.get(base_url + text) as r:
                data = await r.json()
        original = data['contents']['text']
        translated = data['contents']['translated']
        embed = discord.Embed(
            title='Yodish Translator',
            colour=self.colour
        )
        embed.add_field(name='Original',
                        value=original.capitalize(), inline=True)
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
            colour=self.colour,
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
            colour=self.colour
        )
        embed.set_image(url=data)
        await ctx.send(embed=embed)

    @commands.command()
    async def fact(self, ctx):
        async with aiohttp.ClientSession() as cs:
            async with cs.get(f"https://uselessfacts.jsph.pl/random.json?language=en") as r:
                data = await r.json()
        await ctx.send(data["text"])

    @commands.command()
    async def morse(self, ctx, *, text: commands.clean_content):
        """
        Converts the given text into morse code.
        """

        morse_text = ' '.join([self.text_to_morse.get(
            letter.upper(), letter) for letter in str(text).strip()])
        return await ctx.send(f'`{morse_text}`')

    @commands.command()
    async def unmorse(self, ctx, *, morse: commands.clean_content):
        """
        Converts the given morse code into text.
        """

        message = []
        for word in str(morse).strip().split('   '):
            message.append(''.join([self.morse_to_text.get(
                letter.upper(), letter) for letter in word.split()]))
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
