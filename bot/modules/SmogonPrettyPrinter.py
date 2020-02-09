def smogonPrettyPrint(text):
    '''Returns moveset text from Smogon in a pretty format.'''
    pkmn, text    = text.split('@')
    item, text    = text.split('Ability:')
    ability, text = text.split('EVs:')
    text, moves   = text.split('Nature', 1)

    text   = text.replace(' / ', ' ').split(' ')
    nature = text[len(text) - 1]
    text   = text[:-1]
    del(text[0])
    del(text[len(text) -1])
    evs = ''
    for ev in text:
        if ev == '/':
            evs = f'{evs} / '
        evs = f'{evs} {ev}'
    moves = moves.split(' - ')
    del(moves[0])

    message = f'''
__**{pkmn}\:**__
Item    : *{item}*
Ability : *{ability}*
Nature  : *{nature}*
EVs     : *{evs}*

Moves:\n
'''
    for move in moves:
        message = f'''
{message}
    - {move}
'''
    return message