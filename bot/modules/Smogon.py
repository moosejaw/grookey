class Smogon:
    def __init__(self):
        pass

    def prependPokemonName(self, pkmn, text):
        '''Returns the movset text with the Pokémon name prepended.'''
        return f'**__{pkmn}__**\n{text}'

    def prettyPrint(self, text, title=''):
        '''Returns moveset text from Smogon in a pretty format.'''
        pkmn, text    = text.split('@')
        item, text    = text.split('Ability:')
        ability, text = text.split('EVs:')
        text, moves   = text.split('Nature', 1)

        text   = text.replace(' / ', ' ').split(' ')
        nature = text[len(text) - 1]
        text   = text[:-1]
        del(text[0])
        del(text[len(text) - 1])
        evs = ''
        for ev in text:
            if ev == '/':
                evs = f'{evs} / '
            evs = f'{evs} {ev}'
        moves = moves.split(' - ')
        del(moves[0])

        message = \
    f'''{f'> *{title}*' if title else ''}
    **Item\:** {item.strip()}
    **Ability\:** {ability.strip()}
    **Nature\:** {nature.strip()}
    **EVs\:** {evs.strip()}
    **Moves\:**'''
        for move in moves:
            message = f'''{message}
    - {move}'''
        return message