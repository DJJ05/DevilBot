import discord
from discord.ext import commands

import asyncio, aiohttp, io

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
