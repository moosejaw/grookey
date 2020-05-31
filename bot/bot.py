#!/usr/bin/env python3
'''
GrookeyBot for Discord.
'''
import os
import base64
import random
import requests
from time import sleep
from queue import Queue
from datetime import datetime

from PIL import Image, ImageDraw, ImageFont

import discord
from discord.ext import commands

from modules.Emoji import Emoji
from modules.Smogon import Smogon
from modules.Frinkiac import Compuglobal

COMMON_PORT = os.environ['COMMON_PORT']
SMOGON_DNS  = os.environ['SMOGON_DNS']
IMAGE_DIR   = os.environ['IMAGE_DIR']
IMAGE_QUEUE = Queue() # For deleting images sent from frinkiac

def clearImageQueue():
    if not IMAGE_QUEUE.empty():
        while not IMAGE_QUEUE.empty():
            os.remove(IMAGE_QUEUE.get())
            IMAGE_QUEUE.task_done()

def getSmogonInfo(args):
    # TODO: MAKE THE RESPONSE AN EMBED
    # PLEASE IT'S BEGGING FOR IT
    print(f'Started smogon command at {datetime.now().strftime("%H:%M:%S")}', flush=False)
    e = Emoji()
    s = Smogon(SMOGON_DNS, COMMON_PORT)

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
            return e.appendEmoji('grookey', 'Nothing came back from the Node app.')
        
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
        # TODO: change some of these
        return 'res is nothing'
    if res['code'] == 404: 
        return e.appendEmoji('grookey', 'That page doesn\'t exist on Smogon.')
    if res['code'] == 405:
        return e.appendEmoji('grookey', f'Looks like no data exists for {pkmn.capitalize()} in {metagame.upper()} yet.')
    return 'default return'


def getRaidInfo(args):
    # TODO: This
    pass


def getFrinkiacPic(args, futurama=False):
    print(f'Got a request for a frinkiac pic at {datetime.now().strftime("%H:%M:%S")}', flush=False)
    sleep(0.5) # to stop frinkiac telling me off if people are spamming pic requests
    f = Compuglobal() if not futurama \
        else Compuglobal(show='f')
    gif = True if 'g' in args or 'gif' in args \
        else False
    caption = True if 'c' in args  or 'caption' in args \
        else False
    zombie = True if futurama or 'z' in args or 'zombie' in args \
        else False

    if caption and gif:
        return ''

    url, txt = f.getRandomPicURL(use_gif=gif, use_caption=caption, 
        include_zombie=zombie)
    fname = url.split('/')
    fname = f'{IMAGE_DIR}/{fname[len(fname) - 1]}'

    # TODO: Saving to disk here because frinkiac won't allow embedded gifs?
    res = requests.get(url)
    if not res.status_code == 200:
        return 'bad response'
    with open(fname, 'wb') as img:
        img.write(res.content)

    if txt:
        writeTextToPic(fname, txt, futurama)

    print(f'Got the pic at {datetime.now().strftime("%H:%M:%S")}\n', flush=False)
    IMAGE_QUEUE.put(fname)
    return fname


def writeTextToPic(path, text, futurama):
    # Decode the base64 text
    plaintext = base64.b64decode(text).decode() # also converts from bytes to str
    
    image = Image.open(path)
    size = random.randrange(30, 42, 2)
    if futurama: size = size * 3
    font  = ImageFont.truetype("font/AlteHaasGroteskRegular.ttf", size)
    draw  = ImageDraw.Draw(image)
    x, y = [random.randint(10, 200) for i in range(2)]
    draw.text((x, y), plaintext, font=font)
    image.save(path, "JPEG")



if __name__ == '__main__':
    print('hey there. starting up now...', flush=False)
    # Start by getting the token from environment variables
    token = os.environ.get('TOKEN')

    bot = commands.Bot(command_prefix='!')

    # The async functions...
    @bot.command()
    async def hi(ctx):
        await ctx.send('hello!')

    @bot.command()
    async def wat(ctx):
        await ctx.send(embed=discord.Embed(description="You can send simpsons or futurama pic by typing `!s` or `!f` respectively. Use `!s gif` or `!s g` for a GIF (takes a while to send). Use `!s c` for captions. the text is a random size and is placed randomly somewhere in the picture. For the simpsons, use `!s z` to include pics from zombie simpsons in the rng"))

    @bot.command()
    async def smogon(ctx, *args):
        await ctx.send(getSmogonInfo(args))

    @bot.command()
    async def s(ctx, *args):
        path = getFrinkiacPic(args)
        if not path:
            await ctx.send(embed=discord.Embed(description="You can't put captions on a gif yet, sorry"))
        else:
            await ctx.send(file=discord.File(path))
        clearImageQueue()

    @bot.command()
    async def f(ctx, *args):
        path = getFrinkiacPic(args, futurama=True)
        if not path:
            await ctx.send(embed=discord.Embed(description="You can't put captions on a gif yet, sorry"))
        else:
            await ctx.send(file=discord.File(path))
        clearImageQueue()

    # Run the bot
    bot.run(token)
