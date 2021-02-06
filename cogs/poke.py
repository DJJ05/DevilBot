# -*- coding: utf-8 -*-
import asyncio
import csv
import random

import aiocsv
import aiodagpi
import aiofiles
import aiohttp
import discord
import time
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType

from .secrets import secrets_dagpi_token


class pokeCog(commands.Cog):
    """Pokemon commands"""

    def __init__(self, bot):
        self.bot = bot
        self.colour = 0xff9300
        self.dagpi = aiodagpi.AioDagpiClient(secrets_dagpi_token)

    @commands.command(aliases=['mi'])
    async def moveinfo(self, ctx, *, name=None):
        """Get move information. Accepts ID or name, and defaults to a random move"""
        if not self.bot.moves:
            raise commands.BadArgument('Please wait 2-3 seconds to use this command.')

        if not name:
            name = random.choice(list(self.bot.moves.keys()))

        try:
            name = int(name) - 1
        except ValueError:
            ...

        if isinstance(name, int):
            try:
                m = list(self.bot.moves.keys())[name]
                m = self.bot.moves.get(m)
            except:
                raise commands.BadArgument('Unknown move number provided.')
        else:
            name = name.lower().replace(' ', '-').strip()
            try:
                m = self.bot.moves[name]
            except:
                raise commands.BadArgument('Unknown move name provided.')

        em = discord.Embed(
            color=self.colour,
            title=f'Command is WIP, finished soon.',
            description=f''
        )
        return await ctx.send(embed=em)

    @commands.command(aliases=['ai'])
    async def abilityinfo(self, ctx, *, name=None):
        """Get ability information. Accepts ID or name, and defaults to a random ability"""
        if not self.bot.abilities:
            raise commands.BadArgument('Please wait 2-3 seconds to use this command.')

        if not name:
            name = random.choice(list(self.bot.abilities.keys()))

        try:
            name = int(name) - 1
        except ValueError:
            ...

        if isinstance(name, int):
            try:
                a = list(self.bot.abilities.keys())[name]
                a = self.bot.abilities.get(a)
            except:
                raise commands.BadArgument('Unknown ability number provided.')
        else:
            name = name.lower().replace(' ', '-').strip()
            try:
                a = self.bot.abilities[name]
            except:
                raise commands.BadArgument('Unknown ability name provided.')

        em = discord.Embed(
            color=self.colour,
            title=f'{a["name"].replace("-", " ").title()} #{a["id"]}',
            description=f'__**{a["generation"].capitalize()}**__\n{a["description"]}'
        )
        return await ctx.send(embed=em)

    @commands.command(aliases=['d', 'dex', 'pokeinfo', 'pokemoninfo', 'pi'])
    async def pokedex(self, ctx, *, name=None):
        """Get pokedex entry for a pokemon. Defaults to a random pokemon"""
        if not self.bot.pokemon:
            raise commands.BadArgument('Please wait 2-3 seconds to use this command.')

        begin = time.perf_counter()

        if not name:
            name = random.choice(list(self.bot.pokemon.keys()))

        sh = False
        name = name.lower()
        n = ' ' + name.strip()

        if ' mega ' in n:
            n = ' ' + n.replace('mega', '').strip()
            if n.endswith(' x'):
                n = ' ' + n.replace(' x', '').strip()
                n += '-mega-x'
            elif n.endswith(' y'):
                n = ' ' + n.replace(' y', '').strip()
                n += '-mega-y'
            else:
                n += '-mega'

        if ' shiny ' in n:
            n = ' ' + n.replace('shiny', '').strip()
            sh = True

        if ' primal ' in n:
            n = ' ' + n.replace('primal', '').strip()
            n += '-primal'

        if ' alola ' in n or ' alolan ' in n:
            n = ' ' + n.replace('alolan', '').replace('alola', '').strip()
            n += '-alola'

        n = n.strip().replace(' ', '-')

        try:
            p = self.bot.pokemon[n.strip()]
        except:
            raise commands.BadArgument('Unknown Pokémon name provided.')

        typ = p['types'].split('|')
        ty = []
        for t in typ:
            ty.append(f'• {t.capitalize()}')

        abi = p['abilities'].split('|')
        ab = []
        for a in abi:
            ab.append(f'• {a.replace("-", " ").title()}')

        evo = p['evolution'].split('|')
        ev = []
        for e in evo:
            ev.append(f'• {e.capitalize()}')

        name = name.strip().title()
        if ' Shiny ' in name:
            name = name.replace(' Shiny ', ' ')
        if name.startswith('Shiny '):
            name = name.replace('Shiny ', '')
        if sh:
            name = '⭐ ' + name

        end = time.perf_counter()
        rt = round(end - begin, 3) * 1000

        em = discord.Embed(
            color=self.colour,
            title=f'{name} #{p["number"]}',
            description=f'**{p["description"].capitalize()}**'
        )

        em.add_field(name='Height', value=f'{int(p["height"]) / 10}m', inline=True)
        em.add_field(name='Weight', value=f'{int(p["weight"]) / 10}kg', inline=True)
        em.add_field(name='Habitat', value=p['habitat'].capitalize(), inline=True)
        em.add_field(name='Type(s)', value='\n'.join(ty), inline=True)
        em.add_field(name='Abilitites', value='\n'.join(ab), inline=True)
        em.add_field(name='Evolution Line', value='\n'.join(ev), inline=True)
        em.add_field(name='Baby', value=p['baby'], inline=True)
        em.add_field(name='Legendary', value=p['legendary'], inline=True)
        em.add_field(name='Mythical', value=p['mythical'], inline=True)
        em.add_field(name='Capture Rate', value=p["capture"], inline=True)
        em.add_field(name='Generation', value=p['generation'].capitalize(), inline=True)
        em.add_field(name='Response Time', value=str(rt) + 'ms', inline=True)

        if sh:
            em.set_thumbnail(url=p['shiny'])
        else:
            em.set_thumbnail(url=p['sprite'])

        return await ctx.send(embed=em)

    @commands.command(aliases=['refreshmoves', 'um'])
    @commands.is_owner()
    async def updatemoves(self, ctx):
        """Updates the moves csv with the move list"""
        fulldata = []

        async with aiohttp.ClientSession() as c, ctx.typing():
            async with c.get('https://pokeapi.co/api/v2/move?limit=2000') as r:
                ml = await r.json()
                if r.status != 200:
                    return await ctx.send(f'Received {r.status}: {r.reason}')

            mc = ml['count']
            mr = ml['results']

            for m in mr:
                mn = m['name']
                async with c.get(m['url']) as r:
                    mi = await r.json()
                    if r.status != 200:
                        return await ctx.send(f'Received {r.status}: {r.reason}')

                dei = mi['flavor_text_entries']
                de = []
                for du in dei:
                    if du['language']['name'] == 'en':
                        de.append(du['flavor_text'])
                de.sort(key=len)
                de.reverse()

                fd = dict(
                    name=mn,
                    id=mi['id'],
                    accuracy=mi['accuracy'],
                    power=mi['power'],
                    pp=mi['pp'],
                    priority=mi['priority'],
                    target=mi['target']['name'],
                    type=mi['type']['name'],
                    description=de[0] if len(de) else "NULL",
                    damageclass=mi['damage_class']['name'] if mi['damage_class'] else "NULL",
                    generation=mi['generation']['name']
                )

                fulldata.append(fd)

            async with aiofiles.open("moves.csv", mode="w+", encoding="utf-8", newline="") as afp:
                writer = aiocsv.AsyncDictWriter(afp,
                                                ["name", "id", "accuracy", "power", "pp", "priority", "target", "type",
                                                 "description", "damageclass", "generation"], restval="NULL",
                                                quoting=csv.QUOTE_ALL)
                await writer.writeheader()
                await writer.writerows(fulldata)
            return await ctx.send(f'{ctx.author.mention}, successfully inserted `{mc}` entries into `moves.csv`.')

    @commands.command(aliases=['refreshabilities', 'ua'])
    @commands.is_owner()
    async def updateabilities(self, ctx):
        """Updates the abilities csv with the ability list"""
        fulldata = []

        async with aiohttp.ClientSession() as c, ctx.typing():
            async with c.get('https://pokeapi.co/api/v2/ability?limit=2000') as r:
                al = await r.json()
                if r.status != 200:
                    return await ctx.send(f'Received {r.status}: {r.reason}')

            ac = al['count']
            ar = al['results']

            for a in ar:
                an = a['name']
                async with c.get(a['url']) as r:
                    ai = await r.json()
                    if r.status != 200:
                        return await ctx.send(f'Received {r.status}: {r.reason}')

                de = 'NULL'
                for d in ai['effect_entries']:
                    if d['language']['name'] == 'en':
                        de = d['effect']

                fd = dict(
                    name=an,
                    id=ai['id'],
                    generation=ai['generation']['name'],
                    description=de
                )

                fulldata.append(fd)

        async with aiofiles.open("abilities.csv", mode="w+", encoding="utf-8", newline="") as afp:
            writer = aiocsv.AsyncDictWriter(afp,
                                            ["name", "id", "description", "generation"], restval="NULL",
                                            quoting=csv.QUOTE_ALL)
            await writer.writeheader()
            await writer.writerows(fulldata)
        return await ctx.send(f'{ctx.author.mention}, successfully inserted `{ac}` entries into `abilities.csv`.')

    @commands.command(aliases=['refreshpokemon', 'up'])
    @commands.is_owner()
    async def updatepokemon(self, ctx):
        """Updates the pokemon csv with the pokemon list"""
        return
        fulldata = []

        async with aiohttp.ClientSession() as c, ctx.typing():
            async with c.get('https://pokeapi.co/api/v2/pokemon?limit=2000') as r:
                pl = await r.json()
                if r.status != 200:
                    return await ctx.send(f'Received {r.status}: {r.reason}')

            pc = pl['count']
            pli = pl['results']

            for p in pli:
                pn = p['name']
                async with c.get(p['url']) as r:
                    pi = await r.json()
                    if r.status != 200:
                        return await ctx.send(f'Received {r.status}: {r.reason}')

                async with c.get(pi['species']['url']) as r:
                    si = await r.json()
                    if r.status != 200:
                        return await ctx.send(f'Received {r.status}: {r.reason}')

                if si['evolution_chain']:
                    async with c.get(si['evolution_chain']['url']) as r:
                        ec = await r.json()
                        if r.status != 200:
                            return await ctx.send(f'Received {r.status}: {r.reason}')

                pd = 'NULL'
                for ft in si['flavor_text_entries']:
                    if ft['language']['name'] == 'en':
                        pd = ft['flavor_text']

                pe = pn
                if ec:
                    ei = ec['chain']
                    pe = ei['species']['name']
                    if len(ei['evolves_to']):
                        pe += f'|{ei["evolves_to"][0]["species"]["name"]}'
                        if len(ei["evolves_to"][0]["evolves_to"]):
                            pe += f'|{ei["evolves_to"][0]["evolves_to"][0]["species"]["name"]}'

                ps = pn
                if ps.endswith('-x'):
                    ps = ps.replace('-x', 'x')
                if ps.endswith('-y'):
                    ps = ps.replace('-y', 'y')

                fd = dict(
                    name=pn,
                    number=pi['id'],
                    description=pd,
                    height=pi['height'],
                    weight=pi['weight'],
                    types='|'.join(pt['type']['name'] for pt in pi['types']),
                    abilities='|'.join(pa['ability']['name'] for pa in pi['abilities']),
                    evolution=pe,
                    legendary=si['is_legendary'],
                    mythical=si['is_mythical'],
                    baby=si['is_baby'],
                    capture=si['capture_rate'],
                    habitat=si['habitat']['name'] if si['habitat'] else 'NULL',
                    generation=si['generation']['name'],
                    sprite=f'https://projectpokemon.org/images/normal-sprite/{ps}.gif',
                    shiny=f'https://projectpokemon.org/images/shiny-sprite/{ps}.gif'
                )

                fulldata.append(fd)

        async with aiofiles.open("pokemon.csv", mode="w+", encoding="utf-8", newline="") as afp:
            writer = aiocsv.AsyncDictWriter(afp,
                                            ["name", "number", "description", "height", "weight", "types", "abilities",
                                             "evolution", "legendary", "mythical", "baby", "capture", "habitat",
                                             "generation", "sprite", "shiny"], restval="NULL",
                                            quoting=csv.QUOTE_ALL)
            await writer.writeheader()
            await writer.writerows(fulldata)
        return await ctx.send(f'{ctx.author.mention}, successfully inserted `{pc}` entries into `pokemon.csv`.')

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
        emb.description = ''
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
                emb.title = f'Who\'s That Pokemon? You have {3 - tries} guesses left.'
                await mes.edit(embed=emb)
        await ctx.send(f'You ran out of guesses! It was {n_e.capitalize()}.')
        emb.set_image(url=a)
        emb.title = f'Out of guesses! It was {n_e.capitalize()}.'
        return await mes.edit(embed=emb)


def setup(bot):
    bot.add_cog(pokeCog(bot))
