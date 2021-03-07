# -*- coding: utf-8 -*-

import asyncio

from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType


class blackjackCog(commands.Cog):
    """Blackjack, grove_only commands"""

    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        return ctx.guild.id == 696343847210319924

    @commands.group(invoke_without_command=True, aliases=['bj'])
    async def blackjack(self, ctx):
        """Commands for beating unbelievaboat blackjack"""
        await ctx.send_help(ctx.command)

    @blackjack.command()
    @commands.max_concurrency(1, BucketType.member)
    async def solve(self, ctx):
        """To be used before starting a blackjack game"""
        await ctx.message.add_reaction('👍')

        def initial_check(m):
            if m.channel.id == ctx.channel.id:
                if m.author.id == 356950275044671499:
                    if len(m.embeds) > 0:
                        if m.embeds[0].footer.text:
                            if 'Cards remaining' in m.embeds[0].footer.text:
                                if m.embeds[0].author.name:
                                    if m.embeds[0].author.name == str(ctx.author):
                                        if m.embeds[0].colour.value == 240116:
                                            return True
            return False

        def play_check(m):
            if m.channel.id == ctx.channel.id:
                if m.author.id == ctx.author.id:
                    if m.content.lower() in ['hit', 'stand', 'split', 'double down']:
                        return True
            return False

        try:
            msg = await self.bot.wait_for('message', check=initial_check, timeout=30)
        except asyncio.TimeoutError:
            raise commands.BadArgument("You didn't start a blackjack game within 30 seconds, aborting.")

        embed = msg.embeds[0]
        while embed.colour.value == 240116:
            soft_score = False
            player_value = embed.fields[0].value.split(':')[-1].strip()
            bot_value = int(embed.fields[1].value.split(':')[-1].strip().replace('Soft ', ''))
            player_cards = embed.fields[0].value.split('\n')[0].split(' ')
            bot_cards = embed.fields[1].value.split('\n')[0].replace('<:cardBack:418555727376941067>', '').replace('<',
                                                                                                                   '').replace(
                ':', '').strip().split(' ')

            if 'Soft' in player_value:
                soft_score = True
                player_value = int(player_value.replace('Soft ', ''))

            else:
                player_value = int(player_value)

            if player_value == 11:
                recommended_move = 'You should double down if you can afford it.'

            elif player_value == 10 and bot_cards[0][0] not in ('10', 'a', 'j', 'q', 'k'):
                recommended_move = 'You should double down if you can afford it.'

            elif player_value == 9 and bot_cards[0][0] in ('2', '3', '4', '5', '6'):
                recommended_move = 'You should double down if you can afford it.'

            elif len(player_cards) == 2 and player_cards[0][0] == 'a' and player_cards[1][0] == 'a':
                recommended_move = 'You should split.'

            elif len(player_cards) == 2 and player_cards[0][0] == '8' and player_cards[1][0] == '8':
                recommended_move = 'You should split.'

            elif not soft_score and bot_cards[0][0] in ('7', '8', '9', '10', 'a', 'j', 'q', 'k') and player_value < 17:
                recommended_move = 'Don\'t stop hitting until your total is 17 or more.'

            elif not soft_score and bot_cards[0][0] in ('4', '5', '6') and player_value < 12:
                recommended_move = 'Don\'t stop hitting until your total is 12 or more.'

            elif not soft_score and bot_cards[0][0] in ('2', '3') and player_value < 13:
                recommended_move = 'Don\'t stop hitting until your total is 13 or more.'

            elif soft_score and player_value < 18:
                recommended_move = 'Don\'t stop hitting until your total is 18 or more.'

            elif len(player_cards) == 2 and player_cards[0][0] == '2' and player_cards[1][0] == '2' and bot_cards[0][
                0] not in ('8', '9', '10', 'a', 'j', 'q', 'k'):
                recommended_move = 'You should split.'

            elif len(player_cards) == 2 and player_cards[0][0] == '3' and player_cards[1][0] == '3' and bot_cards[0][
                0] not in ('8', '9', '10', 'a', 'j', 'q', 'k'):
                recommended_move = 'You should split.'

            elif len(player_cards) == 2 and player_cards[0][0] == '7' and player_cards[1][0] == '7' and bot_cards[0][
                0] not in ('8', '9', '10', 'a', 'j', 'q', 'k'):
                recommended_move = 'You should split.'

            elif player_value > 16:
                recommended_move = 'You should stand.'

            else:
                recommended_move = 'You should hit.'

            await ctx.send(f'{player_value} against {bot_value}\nRecommended move: `{recommended_move}`')

            try:
                await self.bot.wait_for('message', check=play_check, timeout=60)
            except asyncio.TimeoutError:
                raise commands.BadArgument("You took longer than 60 seconds to play, aborting.")

            await asyncio.sleep(0.5)
            new_msg = await ctx.channel.fetch_message(msg.id)
            embed = new_msg.embeds[0]


def setup(bot):
    bot.add_cog(blackjackCog(bot))
