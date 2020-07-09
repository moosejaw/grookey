#!/usr/bin/env python3
'''
bot for discord.
'''
import os

import discord
from discord.ext import commands

from modules.Emoji import Emoji
from modules.Smogon import Smogon

COMMON_PORT = os.environ['COMMON_PORT']
SMOGON_DNS = os.environ['SMOGON_DNS']


async def send_message_queue(ctx, queue):
    '''Sends all `discord.Embed`s in a queue, eventually clearing it.'''
    while not queue.empty():
        await ctx.send(embed=queue.get())
        queue.task_done()


if __name__ == '__main__':
    # Get token from .env file
    token = os.environ.get('TOKEN')
    bot = commands.Bot(command_prefix='g!')

    @bot.event
    async def on_ready():
        print(r'''
  ___  ____   __    __  __ _  ____  _  _
 / __)(  _ \ /  \  /  \(  / )(  __)( \/ )
( (_ \ )   /(  O )(  O ))  (  ) _)  )  /
 \___/(__\_) \__/  \__/(__\_)(____)(__/ ''', flush=False)
        await bot.change_presence(activity=discord.Game(
            'g!help to show command list!'
            )
        )

    # Smogon: moveset data
    @bot.command()
    async def movesets(ctx, *args):
        s = Smogon(SMOGON_DNS, COMMON_PORT)
        response_queue = s.get_moveset_data(args)
        await send_message_queue(ctx, response_queue)

    # Smogon: pokemon formats
    @bot.command()
    async def formats(ctx, *args):
        s = Smogon(SMOGON_DNS, COMMON_PORT)
        response_queue = s.get_formats(args)
        await send_message_queue(ctx, response_queue)

    # Run the bot
    bot.run(token)
