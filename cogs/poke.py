import aiodagpi
import asyncio
import aiohttp
import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType

from .secrets import secrets_dagpi_token


class pokeCog(commands.Cog):
    """Pokemon commands"""

    def __init__(self, bot):
        self.bot = bot
        self.db_conn = bot.db_conn
        self.colour = 0xff9300
        self.dagpi = aiodagpi.AioDagpiClient(secrets_dagpi_token)

    @commands.command(aliases=['wtp'])
    @commands.cooldown(1, 5, BucketType.user)
    @commands.max_concurrency(1, BucketType.channel)
    async def whosthatpokemon(self, ctx):
        """Starts a game of WhosThatPokemon in the channel executed in."""
        wtp = await self.dagpi.data('wtp', _object=True)
        q = wtp.question
        a = wtp.answer
        n_e = wtp.Data['name'].lower()
        na = []
        async with ctx.typing():
            base_url = 'https://pokeapi.co/api/v2/pokemon/'
            async with aiohttp.ClientSession() as cs:
                try:
                    async with cs.get(base_url + n_e) as r:
                        data = await r.json()
                    species = data['species']['url']
                    async with cs.get(species) as r:
                        data = await r.json()
                    for i in data['names']:
                        na.append(i['name'].lower())
                except:
                    await ctx.send(
                        'Unfortunately I was unable to retrieve multi-lingual names for this pokemon, so you will only be able to answer in english on this occasion.')
                    na.append(n_e)

        def check(m):
            return m.channel.id == ctx.channel.id and m.author.id == ctx.author.id
        tries = 0
        emb = discord.Embed(
            colour=self.colour,
            title='Who\'s That Pokemon?',
            description='You have 3 guesses, or say \'skip\' to skip'
        )
        emb.set_image(url=q)
        mes = await ctx.send(embed=emb)
        while tries < 3:
            try:
                msg = await self.bot.wait_for('message', check=check, timeout=60)
            except asyncio.TimeoutError:
                await ctx.send(f'It\'s been too long since your last guess! It was {n_e.capitalize()}.')
                emb.set_image(url=a)
                emb.title = f'You took too long! It was {n_e.capitalize()}'
                return await mes.edit(embed=emb)
            else:
                if msg.content.lower() == 'skip':
                    await ctx.send(f'Okay, you skipped this one! It was {n_e.capitalize()}.')
                    emb.set_image(url=a)
                    emb.title = f'You skipped! It was {n_e.capitalize()}.'
                    return await mes.edit(embed=emb)
                if msg.content.lower() in na:
                    await ctx.send(f'Correct! It was {n_e.capitalize()}.')
                    emb.set_image(url=a)
                    emb.title = f'You got it! It was {n_e.capitalize()}.'
                    return await mes.edit(embed=emb)
                tries += 1
                emb.title = f'Who\'s That Pokemon? You have {3-tries} guesses left.'
                await mes.edit(embed=emb)
        await ctx.send(f'You ran out of guessed! It was {n_e.capitalize()}.')
        emb.set_image(url=a)
        emb.title = f'Out of guesses! It was {n_e.capitalize()}.'
        return await mes.edit(embed=emb)

    @commands.command(aliases=['mi'])
    async def moveinfo(self, ctx, *, move):
        """Collects information on a specified pokémon move"""
        move = move.lower()
        base_url = 'https://pokeapi.co/api/v2/move/'
        async with aiohttp.ClientSession() as cs, ctx.typing():
            try:
                async with cs.get(base_url + move) as r:
                    data = await r.json()
            except:
                raise commands.BadArgument('Requested move not found!')
        movedesc = data['effect_entries'][0]['effect'].replace(
            '\n', ' ').replace('  ', ' ').capitalize()
        movetype = data['type']['name'].capitalize()
        movepp = data['pp']
        moveid = data['id']
        movepower = data['power']
        movename = data['name'].capitalize()
        movedmgclass = data['damage_class']['name'].capitalize()
        moveaccuracy = data['accuracy']
        movetargets = data['target']['name'].capitalize()
        movegen = data['generation']['name'].capitalize()
        embed = discord.Embed(
            title=f'{movename} #{moveid}',
            colour=self.colour,
            description=f'**{movedesc}**'
        )
        embed.add_field(name=f'Type', value=movetype, inline=True)
        embed.add_field(name=f'PP', value=movepp, inline=True)
        embed.add_field(name=f'Power', value=movepower, inline=True)
        embed.add_field(name=f'Damage Class', value=movedmgclass, inline=True)
        embed.add_field(name=f'Accuracy', value=moveaccuracy, inline=True)
        embed.add_field(name=f'Targets', value=movetargets, inline=True)
        embed.add_field(name=f'Generation', value=movegen, inline=True)
        await ctx.send(embed=embed)

    @commands.command(aliases=['dex'])
    async def pokedex(self, ctx, *, pokemon: str):
        """Return information about specified Pokemon"""
        pokemon = pokemon.lower()
        async with ctx.typing():
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
            pokeweight = f'{data["weight"] / 10}kg'
            poketypes = []
            for i in data['types']:
                poketypes.append(f"• {(i['type']['name'].capitalize())}")
            abilities = []
            for i in data['abilities']:
                abilities.append(f"• {(i['ability']['name'].capitalize())}")
            pokeimg = data['sprites']['other']['official-artwork']['front_default'] or data['sprites']['front_default']
            pokespecies = data['species']['url']
            async with aiohttp.ClientSession() as cs:
                async with cs.get(pokespecies) as r:
                    data = await r.json()
            pokedesc = 'No description found.'
            for i in data['flavor_text_entries']:
                if i['language']['name'] == 'en':
                    pokedesc = (i['flavor_text']).replace(
                        '\n', ' ').lower().capitalize()
                    break
            is_legendary = data['is_legendary']
            is_mythical = data['is_mythical']
            evochain = data['evolution_chain']['url']
            async with aiohttp.ClientSession() as cs:
                async with cs.get(evochain) as r:
                    data = await r.json()
            evoline = f'{data["chain"]["species"]["name"].capitalize()}'
            if len(data['chain']['evolves_to']):
                evoline += f' => {data["chain"]["evolves_to"][0]["species"]["name"].capitalize()}'
                if len(data['chain']['evolves_to'][0]['evolves_to']):
                    evoline += f' => {data["chain"]["evolves_to"][0]["evolves_to"][0]["species"]["name"].capitalize()}'
        embed = discord.Embed(
            title=f'{pokename.capitalize()} {pokenum}',
            colour=self.colour,
            description=f'**{pokedesc.capitalize()}**'
        )
        embed.add_field(name=f'Weight', value=f'{pokeweight}', inline=True)
        embed.add_field(name=f'Height', value=f'{pokeheight}', inline=True)
        embed.add_field(name=f'Type(s)', value="\n".join(
            poketypes), inline=True)
        embed.add_field(name=f'Abilities',
                        value="\n".join(abilities), inline=True)
        embed.add_field(name=f'Evolution Line',
                        value=f'{evoline}', inline=True)
        embed.add_field(name=f'Legendary', value=is_legendary, inline=True)
        embed.add_field(name=f'Mythical', value=is_mythical, inline=True)
        embed.set_image(url=pokeimg)
        return await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(pokeCog(bot))
