class Smogon:
    def __init__(self):
        self.natureStats = {
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

    def prependPokemonAndTier(self, pkmn, text, tier):
        '''Returns the movset text with the Pokémon name prepended.'''
        return f'**__{pkmn}{f'({tier})' if tier else ''}__**\n{text}'

    def prettyPrint(self, text, title=''):
        '''Returns moveset text from Smogon in a pretty format.'''
        text = text.split('\n')

        # Get pokemon and item
        item = None
        pkmn = None
        if '@' in text[0]:
            pkmn, item = text[0].split(' @ ')
        else:
            pkmn = text[0]

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

            nature_spread = self.natureStats[nature.lower()] \
                if nature.lower() in self.natureStats.keys() \
                else None

        # Build the things to print
        to_print = []
        if title: to_print.append(f'> *{title}*')
        if item: to_print.append(f'**Item\:** {item.strip()}')
        if ability: to_print.append(f'**Ability\:** {ability.strip()}')
        if nature: to_print.append(f"**Nature\:** {nature.strip()}{f' ({nature_spread})' if nature_spread else ''}")
        if evs: to_print.append(f'**EVs\:** {evs.strip()}')
        return_msg = to_print[0]
        for part in range(1, len(to_print)):
            return_msg = f'{return_msg}\n{to_print[part]}'
        for move in moves:
            return_msg = f'{return_msg}\n{move}'

        return return_msg