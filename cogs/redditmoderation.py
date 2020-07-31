import discord
from discord.ext import commands

import praw, prawcore
import psycopg2

from .utils import checks
import secrets

class Redditmoderation(commands.Cog):
    """r/Overwatch_Memes Moderation related Commands"""

    def __init__(self, client):
        self.client = client
        self.colour = 0xff9300
        self.footer = 'Bot developed by DevilJamJar#0001\nWith a lot of help from ♿nizcomix#7532'
        self.thumb = 'https://styles.redditmedia.com/t5_3el0q/styles/communityIcon_iag4ayvh1eq41.jpg'

    @commands.command(pass_context=True, aliases=['lb'], invoke_without_command=True)
    @checks.check_mod_server()
    async def leaderboard(self, ctx, amount: int = 10):
        '''Displays moderation leaderboard'''
        if 0 < amount < 20:
            pass
        else:
            return await ctx.send('The limit needs to be between `1` and `19`')
        try:
            connection = psycopg2.connect(user=secrets.secrets_pg_user[0],
                                          password=secrets.secrets_pg_password[0],
                                          host=secrets.secrets_pg_host[0],
                                          port=secrets.secrets_pg_port[0],
                                          database=secrets.secrets_pg_database)

            cursor = connection.cursor()

            sql_select_query = f'SELECT "Mod_Name", ("Flair_Removals" * 5 + "Regular_Removals") AS Removals FROM "ModStatsJuly" ORDER BY Removals DESC LIMIT {amount}'
            cursor.execute(sql_select_query)
            record = cursor.fetchall()
        except Exception as e:
            print (e)
            return await ctx.send(f'Failed to get a valid connection and execution of the database')

        embed=discord.Embed(title=f'Monthly Top {amount} Moderator Actions Leaderboard', color=0xff9300)
        embed.set_thumbnail(url=self.thumb)

        mods = []
        actions = []
        i = []
        for x in range(amount):
            mods.append(record[x][0])
            actions.append(record[x][1])
        for index, value in enumerate(mods, start=1):
            i.append(f"{index}) {value}")
        for mod, action in zip(i, actions):
            embed.add_field(name=mod, value=action, inline=False)
        embed.set_footer(text='Bot developed by DevilJamJar#0001\nWith a lot of help from ♿nizcomix#7532')
                
        await ctx.send(embed=embed)

def setup(client):
    client.add_cog(Redditmoderation(client))