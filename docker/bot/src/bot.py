#!/usr/bin/env python3
import os

import discord
from discord.ext import commands

from modules.Smogon import Smogon
from modules.Exceptions import TokenMissingError

CMD_PREFIX = 'g!'
COMMON_PORT = os.environ['COMMON_PORT']
SMOGON_DNS = os.environ['SMOGON_DNS']


def get_token():
    '''Gets the Discord auth token from environment variables.'''
    try:
        token = os.environ.get('TOKEN')
    except KeyError:
        raise TokenMissingError((
            "The TOKEN environment variable does not exist."
            "Ensure it is set in the .env file."
        ))
    finally:
        if not token:
            raise TokenMissingError((
                "You have not set your token in the .env file."
            ))
    return token


async def send_message_queue(ctx, queue):
    '''Sends all `discord.Embed`s in a queue, eventually clearing it.'''
    while not queue.empty():
        await ctx.send(embed=queue.get())
        queue.task_done()


if __name__ == '__main__':
    # Get token from .env file
    token = get_token()
    bot = commands.Bot(command_prefix=CMD_PREFIX)

    @bot.event
    async def on_ready():
        print(r'''
  ___  ____   __    __  __ _  ____  _  _
 / __)(  _ \ /  \  /  \(  / )(  __)( \/ )
( (_ \ )   /(  O )(  O ))  (  ) _)  )  /
 \___/(__\_) \__/  \__/(__\_)(____)(__/ ''', flush=False)
        await bot.change_presence(activity=discord.Game(
            f'{CMD_PREFIX}help to show command list!'
            )
        )

    # Smogon: moveset data
    @bot.command()
    async def movesets(ctx, *args):
        s = Smogon(SMOGON_DNS, COMMON_PORT)
        response_queue = await s.get_moveset_data(args)
        await send_message_queue(ctx, response_queue)

    # Smogon: pokemon formats
    @bot.command()
    async def formats(ctx, *args):
        s = Smogon(SMOGON_DNS, COMMON_PORT)
        response_queue = await s.get_formats(args)
        await send_message_queue(ctx, response_queue)

    # Smogon: basestats of a poke in a metagame
    @bot.command()
    async def stats(ctx, *args):
        s = Smogon(SMOGON_DNS, COMMON_PORT)
        response_queue = await s.get_basestats(args)
        await send_message_queue(ctx, response_queue)

    @bot.command()
    async def move(ctx, *args):
        s = Smogon(SMOGON_DNS, COMMON_PORT)
        response_queue = await s.get_move(args)
        await send_message_queue(ctx, response_queue)

    # Run the bot
    bot.run(token)
