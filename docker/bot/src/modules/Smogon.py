import random
import discord
import aiohttp
from queue import Queue


class Smogon:
    def __init__(self, cont_dns, cont_port):
        # Container DNS and port
        self.cont_dns = cont_dns
        self.cont_port = cont_port

        # Reference
        self.nature_stats = {
            'lonely': '+Atk -Def',
            'adamant': '+Atk -SpA',
            'naughty': '+Atk -SpD',
            'brave': '+Atk -Spe',
            'bold': '+Def -Atk',
            'impish': '+Def -SpA',
            'lax': '+Def -SpD',
            'relaxed': '+Def -Spe',
            'modest': '+SpA -Atk',
            'mild': '+SpA -Def',
            'rash': '+SpA -SpD',
            'quiet': '+SpA -Spe',
            'calm': '+SpD -Atk',
            'gentle': '+SpD -Def',
            'careful': '+SpD -SpA',
            'sassy': '+SpD -Spe',
            'timid': '+Spe -Atk',
            'hasty': '+Spe -Def',
            'jolly': '+Spe -SpA',
            'naive': '+Spe -SpD'
        }
        self.metagames = {
            'rb': 'R/B/Y',
            'gs': 'G/S/C',
            'rs': 'R/S/E/FR/LG',
            'dp': 'D/P/Pt/HG/SS',
            'bw': 'B/W/B2/W2',
            'xy': 'X/Y/OR/AS',
            'sm': 'S/M/US/UM',
            'ss': 'Sw/Sh'
        }
        self.types = {
            # key = type, value = (hex colour for embed, emoji id) tuple
            'grass': (0xc7ffbd, r'<:grass_sym:675854254602321920>'),
            'water': (0xbff1ff, r'<:water_sym:675854254770094120>'),
            'fire': (0xffc0ba, r'<:fire_sym:675854254535344182>'),
            'ice': (0xbafffa, r'<:ice_sym:675854254597996603>'),
            'poison': (0xd0baff, r'<:poison_sym:675854254891597824>'),
            'psychic': (0xffbadd, r'<:psychic_sym:675854254245675043>'),
            'fairy': (0xfdbdff, r'<:fairy_sym:675854254870888458>'),
            'dragon': (0xbfcaff, r'<:dragon_sym:675854254329561109>'),
            'electric': (0xfffcbd, r'<:electric_sym:675854254518566930>'),
            'bug': (0xdcffbd, r'<:bug_sym:675854254526693424>'),
            'fighting': (0xd4ad9b, r'<:fighting_sym:675854254551859200>'),
            'ghost': (0x696a8c, r'<:ghost_sym:675854254577287189>'),
            'dark': (0x3b3c47, r'<:dark_sym:675854254187085836>'),
            'rock': (0x5c534f, r'<:rock_sym:675854254623162374>'),
            'steel': (0xd6d3d2, r'<:steel_sym:675854254837334038>'),
            'flying': (0xc9deff, r'<:flying_sym:675854254740602880>'),
            'ground': (0x9c6f51, r'<:ground_sym:675854254597996584>')
        }
        self.retry_lim = 3  # number of times to retry sending requests

        # Embed properties
        self.error_colour = 0xe42e2e

    async def call(self, params, endpoint):
        '''
        Sends an API call to the Smogon container at the given
        endpoint and returns the appropriate response.

        Parameters:
            params (dict): Dictionary containing the expected
            parameters. e.g. {'pkmn': 'grookey', 'metagame': 'ss'}

            endpoint (string): String corresponding to the endpoint
            to be called. e.g. 'movesets'

        Returns:
            The JSON response (as dict) if response code == 200.
            Otherwise a discord.Embed is returned with the appropriate
            error message corresponding to the response code.
        '''
        # Get the response from the docker container
        async with aiohttp.ClientSession() as s:
            res = None
            for i in range(self.retry_lim):
                async with s.get(
                    f'http://{self.cont_dns}:{self.cont_port}/{endpoint}/',
                    params=params
                ) as r:
                    res = await r.json()
                    if not res:
                        if i <= self.retry_lim:
                            continue
                        else:
                            # No response at all, used up all retries
                            return discord.Embed(
                                title="No response!",
                                description=(
                                    "Didn't get a response from the Smogon"
                                    " API container. Is it running?"
                                ),
                                color=self.error_colour
                            )
                    else:
                        break

        # Handle non-200 responses
        if res['code'] == 404:
            return discord.Embed(
                title="Page not found!",
                description=(
                    "Smogon returned a 404 (page not found) error."
                    " Did you spell everything correctly?"
                ),
                color=self.error_colour
            )
        elif res['code'] == 405:
            return discord.Embed(
                title="No moveset data!",
                description=(
                    "Looks like no moveset data exists for "
                    "that Pokémon (yet). Sorry!"
                ),
                color=self.error_colour
            )
        elif res['code'] != 200:
            return discord.Embed(
                title="Unexpected response!",
                description=(
                    "Got an unexpected response code: "
                    f"{res['code']}"
                ),
                color=self.error_colour
            )

        # On success
        return res

    async def get_moveset_data(self, args):
        message_queue = Queue()

        # Validation
        arg_validation = await self.validate_args(args)
        if arg_validation is not True:
            message_queue.put(arg_validation)
            return message_queue

        # TODO: Get emojis working here?
        # e = Emoji()

        # Parse the args
        metagame, pokemon = await self.parse_args(args)

        # Make API call
        response = await self.call(
            {'pkmn': pokemon, 'metagame': metagame},
            'movesets'
        )
        if not isinstance(response, dict):
            # Return error messages
            message_queue.put(response)
            return message_queue
        else:
            # Build the embed(s) containing the data
            tier = response['tier']
            colour = self.types[response['types'][0]][0]  # based on first type

            # Add types
            type_symbols = response['types'][0].capitalize()
            if len(response['types']) == 2:
                type_symbols = (
                    type_symbols +
                    ' / ' +
                    response['types'][1].capitalize()
                )

            # Build the embed
            for data, title in list(zip(response['data'], response['titles'])):
                embed = discord.Embed(
                    title=title,
                    color=colour,
                    description=(
                        f'{pokemon.lower().capitalize()}'
                        f'{f" [{tier.upper()}]" if tier else ""}'
                    ),
                    url=response['url']
                )
                embed.add_field(
                    name='Type',
                    value=type_symbols,
                    inline=True
                )

                # Attach thumbnail
                t_url = await self.get_thumbnail_url(pokemon, metagame)
                embed.set_thumbnail(
                    url=t_url
                )

                # Parse data and build embed
                data = await self.parse_moveset_data(data)
                for field, value in data.items():
                    embed.add_field(
                        name=field,
                        value=value,
                        inline=True if field != 'Moves' else False
                    )
                message_queue.put(embed)
            return message_queue

    async def parse_moveset_data(self, text):
        '''Returns moveset data from Smogon in a dict.'''
        # TODO: make better
        text = text.split('\n')

        # Get pokemon and item
        item = None
        if '@' in text[0]:
            item = text[0].split(' @ ')[1]

        pre_gen_three = False
        moves = []

        line_with_evs = 2
        line_with_nature = 3
        first_move_line = 4

        # Get moves if gen 1
        ability = None
        if text[1].startswith('-'):
            pre_gen_three = True
            moves = text[1:]
        # Otherwise get ability
        else:
            if 'Ability' in text[1]:
                ability = text[1].split('Ability: ')[1]
            else:
                # No ability in moveset data but pkmn is > gen 3
                line_with_evs -= 1
                line_with_nature -= 1
                first_move_line -= 1

        # Get EVs and nature if < gen 3
        evs = None
        nature = None
        if not pre_gen_three:
            evs = text[line_with_evs].split('EVs:')[1]
            nature = text[line_with_nature].split(' Nature')[0].strip()
            moves = text[first_move_line:]

            nature_spread = self.nature_stats[nature.lower()] \
                if nature.lower() in self.nature_stats.keys() \
                else None

        if nature_spread and nature:
            nature = f'{nature} ({nature_spread})'

        moves_string = ''
        first_move = True
        for m in moves:
            if first_move:
                moves_string = m
                first_move = False
            else:
                moves_string = f'{moves_string}\n{m}'

        # Build dict containing data and return
        # TODO: make less ugly
        d = {}
        if item:
            d['Item'] = item.strip()
        if nature:
            d['Nature'] = nature.strip()
        if ability:
            d['Ability'] = ability.strip()
        if evs:
            d['EVs'] = evs.strip()
        d['Moves'] = moves_string
        return d

    async def get_formats(self, args):
        message_queue = Queue()
        # Validation
        arg_validation = await self.validate_args(args)
        if arg_validation is not True:
            message_queue.put(arg_validation)
            return message_queue

        # Parse args
        metagame, pokemon = await self.parse_args(args)

        # Make API call
        response = await self.call(
            {'pkmn': pokemon, 'metagame': metagame},
            'formats'
        )
        if not isinstance(response, dict):
            # Return error messages
            message_queue.put(response)
            return message_queue
        else:
            desc = (
                f'For {self.metagames[metagame]}, {pokemon.capitalize()} '
                ' has the following formats:\n'
            )
            for fmt in response['data']:
                desc = desc + f' `{fmt}`'
            embed = discord.Embed(
                title=f'{pokemon.capitalize()} [{metagame.upper()}]',
                description=desc,
                url=response['url']
            )
            t_url = await self.get_thumbnail_url(pokemon, metagame)
            embed.set_thumbnail(
                url=t_url
            )
            message_queue.put(embed)
            return message_queue

    async def get_thumbnail_url(self, pokemon, metagame):
        '''Returns the URL of the thumbnail of a given Pokemon.'''
        extension = "gif"
        if metagame == 'dp' or metagame == 'rb' or metagame == 'rs':
            extension = "png"
        url_metagame = metagame
        if metagame == 'sm' or metagame == 'ss':
            url_metagame = 'xy'
        return (
            "https://www.smogon.com/dex/media/sprites/"
            f"{url_metagame}/{pokemon}.{extension}"
        )

    async def validate_args(self, args, expected_len=2):
        '''
        Validates the arguments given for a Pokemon and a metagame.
        Returns True if arguments are valid, a Discord embed describing
        the error if not.
        '''
        # Not enough arguments
        if len(args) != expected_len:
            embed = await self.add_metagames_to_embed(
                discord.Embed(
                    title="Not enough arguments!",
                    description=(
                        "Make sure you include a Pokémon and "
                        "a metagame in your command."
                    ),
                    color=self.error_colour
                )
            )
            return embed

        # Metagame isn't two letters long
        elif not list(filter(lambda x: len(x) == 2, args)):
            embed = await self.add_metagames_to_embed(
                discord.Embed(
                    title="Invalid metagame argument!",
                    description="Make sure you include a valid metagame.",
                    color=self.error_colour
                )
            )
            return embed
        else:
            return True

    async def parse_args(self, args):
        '''
        Parses the arguments given and returns them in a tuple
        in the format (metagame, pokemon)
        '''
        args = list(map(lambda x: str(x).lower(), args))
        if args[0] not in self.metagames.keys():
            metagame = args[1]
            pokemon = args[0]
        else:
            metagame = args[0]
            pokemon = args[1]
        return (metagame, pokemon)

    async def add_metagames_to_embed(self, embed):
        '''Adds all the possible metagame combinations to a discord.Embed'''
        for key, value in self.metagames.items():
            embed.add_field(
                name=value,
                value=f'`{key}`',
                inline=True
            )
        embed.set_footer(
            text=(
                "These are the valid metagames you can choose from."
                " A valid command looks like `!smogon grookey ss`"
            )
        )
        return embed
