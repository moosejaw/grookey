#!/usr/bin/env python3
'''
GrookeyBot for Discord.
'''
import os
from datetime import datetime

import discord
from discord.ext import commands

from modules.Emoji import Emoji
from modules.Smogon import Smogon

SMOGON_DNS  = os.environ['SMOGON_DNS']
SMOGON_PORT = os.environ['SMOGON_PORT']

def getSmogonInfo(args):
    print(f'Started smogon command at {datetime.now().strftime("%H:%M:%S")}', flush=False)
    e = Emoji()
    s = Smogon(SMOGON_DNS, SMOGON_PORT)

    # Bad args
    if len(args) != 2:
        return e.appendEmoji('grookey', 'Enter the command in the format: pokémon metagame, e.g. `grookey ss`')

    # Parse the args
    pkmn, metagame = args
    params = {'pkmn': pkmn.lower(), 'metagame': metagame.lower()}
    
    # Get the response
    retry_lim = 3
    res       = None
    for i in range(retry_lim):
        print(f'Sending request at {datetime.now().strftime("%H:%M:%S")}', flush=False)
        res = s.getNodeResponse(params)
        print(f'Request came back at {datetime.now().strftime("%H:%M:%S")}', flush=False)

        if not res:
            return e.appendEmoji('grookey', 'Nothing came back from Node.')
        
        if res["code"] == 404:
            print(f'Got a 404 response at {datetime.now().strftime("%H:%M:%S")} so sending the response again', flush=False)
            continue
        else:
            break

    # On success
    if res['code'] == 200:
        msg = ''
        for m, t in list(zip(res['msgs'], res['titles'])):
            msg = f'{msg}{s.prettyPrint(m, title=t)}\n\n'
        msg = s.prependPokemonAndTier(pkmn.lower().capitalize(), msg, res['tier'])
        msg = e.appendEmoji("koffing", msg, prepend=True)

        print(f'Done preparing the message at {datetime.now().strftime("%H:%M:%S")}', flush=False)
        return msg

    # Rejectors
    if not res:
        return 'res is nothing'
    if res['code'] == 404: 
        return e.appendEmoji('grookey', 'That page doesn\'t exist on Smogon.')
    if res['code'] == 405:
        return e.appendEmoji('grookey', f'Looks like no data exists for {pkmn.capitalize()} in {metagame.upper()} yet.')
    return 'default return'

def getRaidInfo(args):
    pass
    # blah blah ...

if __name__ == '__main__':
    print('hey there. starting up now...', flush=False)
    # Start by getting the token from environment variables
    token = os.environ.get('TOKEN')

    bot = commands.Bot(command_prefix='!g ')

    # The async functions...
    @bot.command()
    async def hi(ctx):
        await ctx.send('hello!')

    @bot.command()
    async def smogon(ctx, *args):
        await ctx.send(getSmogonInfo(args))

    # Run the bot
    bot.run(token)
