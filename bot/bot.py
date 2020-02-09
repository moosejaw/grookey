#!/usr/bin/env python3
'''
GrookeyBot for Discord.
'''
import os
import queue
import getpass
import requests

import discord
from discord.ext import commands

from modules.Emoji import Emoji
from modules.SmogonPrettyPrinter import smogonPrettyPrint

SMOGON_DNS  = 'smogon'
SMOGON_PORT = os.environ['SMOGON_PORT']
SMOGON_DEX_URL = 'https://www.smogon.com/dex/'
SMOGON_QUEUE   = queue.Queue(maxsize=500)

def getNodeResponse(params):
    '''Send a request to the node server. Sorta.'''
    r = requests.get(f'http://{SMOGON_DNS}:{SMOGON_PORT}/api/', params=params)
    if not r.text: 
        return 'Nothing came back from the server.'
    return r.text

def getSmogonInfo(args):
    e = Emoji()
    if len(args) != 2:
        return e.appendEmoji('grookey', 'Enter the command in the format: pokémon metagame, e.g. `grookey ss`')

    pkmn, metagame = args
    params = {'pkmn': pkmn, 'metagame': metagame}
    
    # Get the response
    res = getNodeResponse(params)
    if res == '404': 
        return e.appendEmoji('grookey', 'That page doesn\'t exist on Smogon.')
    return e.appendEmoji('koffing', smogonPrettyPrint(res))

def getRaidInfo(args):
    e = Emoji()
    if len(args) != 1:
        err = f'some error'
        return err

    # Build the url for smogon
    gen, pkmn = args
    url = f'{SMOGON_DEX_URL}/{gen}/pokemon/{pkmn}'
    return e.appendEmoji('koffing', 'Smogon says...')
    # blah blah ...



# Main
if __name__ == '__main__':
    # Start by getting the token from environment variables
    token = os.environ.get('TOKEN')

    bot = commands.Bot(command_prefix='!grookey ')

    # The async functions...
    @bot.command()
    async def hi(ctx):
        await ctx.send('hello there!')

    @bot.command()
    async def smogon(ctx, *args):
        await ctx.send(getSmogonInfo(args))

    @bot.command()
    async def raids(ctx, *args):
        await ctx.send(getRaidInfo(args))

    @bot.command()
    async def testsocket(ctx, *args):
        await ctx.send(getSmogonInfo(args))

    # Run the bot
    bot.run(token)
