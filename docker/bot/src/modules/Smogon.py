import re
import random
import discord
import aiohttp
from queue import Queue
from .Emotes import Emotes


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
            'ground': (0x9c6f51, r'<:ground_sym:675854254597996584>'),
            'normal': (0xe3e3e3, r'<:normal_sym:675854254740865024>')
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
            # FIXME: pep8
            desc = "Smogon returned a 404 (page not found) error. Did you spell everything correctly?"
            if endpoint == 'ability' or endpoint == 'move':
                desc = f'{desc}\nIt is possible that what you have searched doesn\'t exist in this metagame. Try a different metagame maybe?'
            return discord.Embed(
                title="Page not found!",
                description=desc,
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

    async def get_test(self, args):
        message_queue = Queue()

        # Process args
        args = await self.process_args(args)
        if not isinstance(args, tuple):
            message_queue.put(args)
            return message_queue

        # Unpack args and make API call
        metagame, move = args
        response = await self.call(
            {'move': move, 'metagame': metagame},
            'test'
        )
        if not isinstance(response, dict):
            message_queue.put(response)
            return message_queue
        else:
            message_queue.put(response['data'])
            return message_queue

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
            tier = response['data']['tier']
            colour = self.types[response['data']['types'][0]][0]  
            # based on first type

            # Add types
            type_symbols = response['data']['types'][0].capitalize()
            if len(response['data']['types']) == 2:
                type_symbols = (
                    type_symbols +
                    ' / ' +
                    response['data']['types'][1].capitalize()
                )

            # Build the embed
            for data, title in list(zip(
                response['data']['movesets'], response['data']['titles']
            )):
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
                data = await self.parse_moveset_data(data, metagame)
                for field, value in data.items():
                    embed.add_field(
                        name=field,
                        value=value,
                        inline=True if field != 'Moves' else False
                    )
                message_queue.put(embed)
            return message_queue

    async def parse_moveset_data(self, text, metagame):
        '''
        Returns moveset data from Smogon in a dictionary corresponding to each
        relvant field. The 'moveset data' being parsed in this context is the
        text one would see if they go to a Pokemon's movesets page and click
        the 'Export' button next to a moveset.
        '''
        # TODO: Make DRY
        data = {}
        text = text.split('\n')  # Split the moveset text into separate lines

        # Non-gen 1 pokemon
        if not metagame == 'rb':
            # Get moves into a separate list for convenience
            moves_line = 0
            for i in range(len(text)):
                if re.match(r'^-', text[i]):
                    text, moves = text[:i], text[i:]
                    break

            # Set the item if the pokemon has one
            if '@' in text[0]:
                data['Item'] = text[0].split(' @ ')[1]
            text.pop(0)

            for line in text:
                if ':' in line:
                    f, v = line.split(':')
                    data[f] = v.strip()
                else:
                    nat = line.split(' ')[0]
                    if nat.lower() in self.nature_stats.keys():
                        nat = nat + f' ({self.nature_stats[nat.lower()]})'
                    data['Nature'] = nat

            # Parse the moves
            moves = list(map(lambda x: x + '\n', moves))
            data['Moves'] = ''.join(moves)
            return data
        else:
            # Pokemon is from gen 1 so just get the moves
            # and return those (no items, abilities, etc exist)
            text.pop(0)
            text = list(map(lambda x: x + '\n', text))
            data['Moves'] = ''.join(text)
            return data

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
            for fmt in response['data']['formats']:
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

    async def get_move(self, args):
        '''
        Returns the Smogon entry for a particular move.
        '''
        message_queue = Queue()

        # Process args
        args = await self.process_args(args)
        if not isinstance(args, tuple):
            message_queue.put(args)
            return message_queue

        # Unpack args and make API call
        metagame, move = args
        response = await self.call(
            {'move': move, 'metagame': metagame},
            'move'
        )
        if not isinstance(response, dict):
            message_queue.put(response)
            return message_queue
        else:
            embed = discord.Embed(
                title=f'{move.capitalize()} ({metagame.upper()})',
                description=response['data']['description'],
                color=self.types[response['data']['type'].lower()][0],
                url=response['url']
            )
            del response['data']['move']
            del response['data']['description']
            for field, value in response['data'].items():
                embed.add_field(
                    name=field.capitalize() if field != 'pp'
                    else field.upper(),
                    value=value
                )
            message_queue.put(embed)
            return message_queue

    async def get_ability(self, args):
        '''
        Returns a description of a specific ability from
        a given metagame.
        '''
        message_queue = Queue()

        # Validate args
        args_valid = await self.validate_args(args)
        if args_valid is not True:
            message_queue.put(args_valid)
            return message_queue

        # Parse args
        metagame, ability = await self.parse_args(args)

        if metagame == 'rb' or metagame == 'gs':
            embed = discord.Embed(
                title="Invalid metagame!",
                description=(
                    "Abilities are only in `rs` (Ruby/Sapphire/Emerald) "
                    "and later."
                ),
                color=self.error_colour
            )
            message_queue.put(embed)
            return message_queue

        # Call
        response = await self.call(
            {'ability': ability, 'metagame': metagame},
            'ability'
        )
        if not isinstance(response, dict):
            message_queue.put(response)
            return message_queue
        else:
            # Build the embed
            embed = discord.Embed(
                title=f'{ability.capitalize()} ({metagame.upper()})',
                description=response['data']['description'],
                url=response['url'],
                color=0xe3e3e3
            )
            message_queue.put(embed)
            return message_queue

    async def get_basestats(self, args):
        '''
        Returns a Pokemon's base stats from a given metagame.
        '''
        message_queue = Queue()

        # Validate args
        args_valid = await self.validate_args(args)
        if args_valid is not True:
            message_queue.put(args_valid)
            return message_queue

        # Parse args
        metagame, pokemon = await self.parse_args(args)

        # Call
        response = await self.call(
            {'pkmn': pokemon, 'metagame': metagame},
            'basestats'
        )
        if not isinstance(response, dict):
            message_queue.put(response)
            return message_queue
        else:
            # Build the embed
            colour = self.types[response['data']['types'][0]][0]
            stat_total = sum([int(i[1]) for i in response['data']['stats']])

            # Get stat bars
            desc = f'**Total: {stat_total}**\n'
            for stat in response['data']['stats']:
                bar = await self.get_stat_emote_string(
                    stat[1]
                )
                desc = (
                    f'{desc}'
                    f'{stat[0]}: {bar} **{stat[1]}**'
                    '\n'
                )
            embed = discord.Embed(
                title=f'{pokemon.capitalize()} ({metagame.upper()}) Stats',
                description=desc,
                url=response['url'],
                color=colour
            )
            t_url = await self.get_thumbnail_url(pokemon, metagame)
            embed.set_thumbnail(
                url=t_url
            )
            message_queue.put(embed)
            return message_queue

    async def get_stat_emote_string(self, stat_value):
        '''Returns a string containing the base stat bar emote
        based on the magnitude of the stat.'''
        e = Emotes()
        stat_value = int(stat_value)
        scale = int(stat_value / 20)
        if stat_value < 60:
            bar_col = 'r'
        elif 60 <= stat_value < 80:
            bar_col = 'o'
        elif 80 <= stat_value < 90:
            bar_col = 'y'
        elif 90 <= stat_value < 110:
            bar_col = 'pg'
        else:
            bar_col = 'bg'
        bar = e.stat_emotes[bar_col]
        return ''.join([bar for i in range(scale)])

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

    async def process_args(self, args, expected_len=2):
        '''
        Helper function to process the arguments of an input.
        '''
        args_valid = await self.validate_args(args)
        if args_valid is not True:
            return args_valid
        arg_list = await self.parse_args(args)
        return arg_list

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
        # TODO: accept args with more than one word.. eg 'ROCK SMASH' or 'IRON BARBS'
        # make it so you don't have to use dashes!
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
