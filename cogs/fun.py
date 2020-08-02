import discord
from discord.ext import commands

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

def setup(bot):
    bot.add_cog(funCog(bot))
