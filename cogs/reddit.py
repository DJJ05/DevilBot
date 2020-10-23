import discord
from discord.ext import commands
import secrets

import asyncpraw
import random
import aiohttp

reddit = asyncpraw.Reddit(client_id=secrets.secrets_asyncpraw_client_id,
                          client_secret=secrets.secrets_asyncpraw_client_secret,
                          password=secrets.secrets_asyncpraw_password,
                          user_agent=secrets.secrets_asyncpraw_user_agent,
                          username=secrets.secrets_asyncpraw_username)


class redditCog(commands.Cog):
    """Reddit commands"""

    def __init__(self, bot):
        self.bot = bot
        self.db_conn = bot.db_conn
        self.colour = 0xff9300
        self.footer = 'Bot developed by DevilJamJar#0001\nWith a lot of help from ♿nizcomix#7532'
        self.thumb = 'https://styles.redditmedia.com/t5_3el0q/styles/communityIcon_iag4ayvh1eq41.jpg'

    # Code used from niztg's CyberTron5000 GitHub Repository Provided by the MIT License
    # https://github.com/niztg/CyberTron5000/blob/master/CyberTron5000/cogs/reddit.py#L83-L105
    # Copyright (c) 2020 niztg

    @commands.command(aliases=['maymay'])
    async def meme(self, ctx):
        subreddit = random.choice(
            [
                'memes', 'dankmemes', 'dankexchange', 'okbuddyretard', 'wholesomememes'
            ]
        )
        memes = []
        async with ctx.typing():
            subreddit = await reddit.subreddit(subreddit)
            async for submission in subreddit.hot(limit=50):
                if not submission.over_18 and not submission.distinguished and not submission.is_self:
                    memes.append(submission)
        submission = random.choice(memes)
        embed = discord.Embed(
            colour=self.colour,
            title=submission.title.capitalize(),
            url=f'https://reddit.com{submission.permalink}',
            description=f'Posted in r/{subreddit} by u/{submission.author.name}\n\n\
                              <:upvote:748924744572600450> {submission.score}   <:speechbubble:748960649861922877> {submission.num_comments}'
        )
        embed.set_image(url=submission.url)
        await ctx.send(embed=embed)

    @commands.command()
    async def showerthought(self, ctx):
        thoughts = []
        async with ctx.typing():
            subreddit = await reddit.subreddit('showerthoughts')
            async for submission in subreddit.hot(limit=50):
                if not submission.over_18 and not submission.distinguished and submission.is_self:
                    thoughts.append(submission)
        submission = random.choice(thoughts)
        embed = discord.Embed(
            colour=self.colour,
            title=f'Showerthought by u/{submission.author.name}',
            url=f'https://reddit.com{submission.permalink}',
            description=f'```fix\n{submission.title.capitalize()}\n```\n<:upvote:748924744572600450> {submission.score}   <:speechbubble:748960649861922877> {submission.num_comments}'
        )
        embed.set_image(url=submission.url)
        await ctx.send(embed=embed)

    @commands.command()
    async def askreddit(self, ctx):
        qs = []
        async with ctx.typing():
            subreddit = await reddit.subreddit('askreddit')
            async for submission in subreddit.hot(limit=50):
                if not submission.over_18 and not submission.distinguished and submission.is_self:
                    qs.append(submission)
        submission = random.choice(qs)
        subcomments = await submission.comments()
        embed = discord.Embed(
            title=submission.title.capitalize(),
            colour=self.colour,
            url=f'https://reddit.com{submission.permalink}',
            description=f'<:upvote:748924744572600450> {submission.score}   <:speechbubble:748960649861922877> {submission.num_comments}'
        )
        embed.add_field(
            name=f'Top Comment:',
            value=f'```fix\n{subcomments[0].body[:1010]}\n```',
            inline=False
        )
        embed.add_field(
            name=f'Random Comment:',
            value=f'```fix\n{random.choice(subcomments).body[:1010]}\n```',
            inline=False
        )
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(redditCog(bot))
