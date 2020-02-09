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

SMOGON_DNS  = 'smogon'
SMOGON_PORT = os.environ['smogonport']
SMOGON_DEX_URL = 'https://www.smogon.com/dex/'
SMOGON_QUEUE   = queue.Queue(maxsize=500)

def getSmogonInfo(args):
    e = Emoji()
    if len(args) != 2:
        return e.appendEmoji('grookey', 'Enter the command in the format: pokémon generation, e.g. grookey ss')
    return e.appendEmoji('grookey', 'Smogon stuff will go here.')

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

def getNodeResponse(args):
    '''Send a request to the node server. Sorta.'''
    r = requests.get('smogon:8888/api/')
    return r.text
    

# Main
if __name__ == '__main__':
    # Start by getting the token from environment variables
    token = os.environ.get('token')

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
        await ctx.send(getNodeResponse(args))

    # Run the bot
    bot.run(token)