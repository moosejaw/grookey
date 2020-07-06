import discord
import requests
from queue import Queue

class Smogon:
    def __init__(self, cont_dns, cont_port, args):
        self.args = args

        # Container DNS and port
        self.cont_dns    = cont_dns
        self.cont_port   = cont_port

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
        self.metagames = [
            'rb', 'gs', 'rs', 'dp', 'bw', 'xy', 'sm', 'ss'
        ]
        self.retry_lim = 3 # number of times to retry sending requests

        # Embed properties
        self.error_colour  = 0xe42e2e
        self.smogon_colour = 0x8562a4

    def getData(self, params):
        '''Call the Smogon API through the docker container.'''
        r = requests.get(f'http://{self.cont_dns}:{self.cont_port}/api/', params=params)
        if not r.json(): 
            return None
        return r.json()

    def getMovesetData(self):
        message_queue = Queue()

        # Not enough arguments
        if len(self.args) != 2:
            embed = self.addMetagamesToEmbed(\
                discord.Embed(title="Not enough arguments!", \
                    description="Make sure you include a Pokémon and a metagame in your command."))
            message_queue.put(embed)
            return message_queue
        # Metagame isn't two letters long
        elif not list(filter(lambda x: len(x) == 2, self.args)):
            embed = self.addMetagamesToEmbed(\
                discord.Embed(title="Invalid metagame argument!", \
                    description="Make sure you include a valid metagame."))
            message_queue.put(embed)
            return message_queue

        # TODO: Get emojis working here
        #e = Emoji()

        # Parse the args
        args = list(map(lambda x: str(x).lower(), self.args))
        if args[0] not in self.metagames:
            metagame = args[1]
            pokemon  = args[0]
        else:
            metagame = args[0]
            pokemon = args[1]

        params = {'pkmn': pokemon, 'metagame': metagame}
        
        # Get the response from the docker container
        res = None
        for i in range(self.retry_lim):
            r = requests.get(f'http://{self.cont_dns}:{self.cont_port}/api/', params=params)
            if not r.json():
                if i < self.retry_lim:
                    continue 
                else:
                    return discord.Embed(title="No response!", 
                        description="Didn't get a response from the Smogon API container. Is it running?", 
                        color=self.error_colour)
            else:
                res = r.json()
                break

        # Send an error if a 404 or 405 came back
        if res['code'] == 404:
            embed = discord.Embed(title="Page not found!",
                description="Smogon returned a 404 (page not found) error. Did you spell everything correctly?",
                color=self.error_colour)
            message_queue.put(embed)
            return message_queue
        elif res['code'] == 405:
            embed = discord.Embed(title="No moveset data!",
                description="Looks like no moveset data exists for that Pokémon (yet). Sorry!",
                color=self.error_colour)
            message_queue.put(embed)
            return message_queue

        # On success
        if res['code'] == 200:
            tier = res['tier']
            for data, title in list(zip(res['data'], res['titles'])):
                embed = discord.Embed(title=title, color=self.smogon_colour)
                embed.set_author(name=f'{pokemon.lower().capitalize()}{f" [{tier.upper()}]" if tier else ""} ({metagame.upper()})', 
                url=res['url'])

                # Parse data and build embed
                data = self.parseMovesetData(data)
                for field, value in data.items():
                    embed.add_field(name=field, value=value, inline=True)
                message_queue.put(embed)
            return message_queue
        
        # Fallback
        embed = discord.Embed(title="Unexpected API return!",
            description="The Smogon API container did something I wasn\'t expecting.",
            color=self.error_colour)
        message_queue.put(embed)
        return message_queue

    def getEmbedTitle(self, pkmn, tier, metagame):
        '''Returns the movset text with the Pokémon name prepended.'''
        return f'{pkmn.lower().capitalize()}{f" [{tier.upper()}]" if tier else ""} ({metagame.upper()})'

    def parseMovesetData(self, text):
        '''Returns moveset data from Smogon in a dictionary.'''
        text = text.split('\n')

        # Get pokemon and item
        item = None
        if '@' in text[0]:
            item = text[0].split(' @ ')[1]

        pre_gen_three = False
        moves = []

        line_with_evs    = 2
        line_with_nature = 3
        first_move_line  = 4

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
        first_move   = True
        for m in moves: 
            if first_move:
                moves_string = m
                first_move = False
            else:
                moves_string = f'{moves_string}\n{m}'

        # Build dict containing data and return
        # TODO: make less ugly
        d = {}
        if item: d['Item'] = item.strip()
        if nature: d['Nature'] = [nature.strip()]
        if nature_spread: d['Nature'].append(nature_spread)
        if ability: d['Ability'] = ability.strip()
        if evs: d['EVs'] = evs.strip()
        d['Moves'] = moves_string
        return d

    def addMetagamesToEmbed(self, embed):
        '''Adds all the possible metagame combinations to a discord.Embed'''
        embed.add_field(name="Red/Blue", value="`rb`", inline=True)
        embed.add_field(name="Gold/Silver/Crystal", value="`gs`", inline=True)
        embed.add_field(name="Ruby/Sapphire/Emerald", value="`rs`", inline=True)
        embed.add_field(name="Diamond/Pearl/Platinum", value="`dp`", inline=True)
        embed.add_field(name="Black/White/Black 2/White 2", value="`bw`", inline=True)
        embed.add_field(name="X/Y", value="`xy`", inline=True)
        embed.add_field(name="Sun/Moon/Ultra Sun/Ultra Moon", value="`sm`", inline=True)
        embed.add_field(name="Sword/Shield", value="`ss`", inline=False)
        embed.set_footer(text="These are the valid metagames you can choose from. A valid command looks like `!smogon grookey ss`")
        return embed