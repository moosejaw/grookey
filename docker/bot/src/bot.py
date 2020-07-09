#!/usr/bin/env python3
'''
bot for discord.
'''
import os
import re
import base64
import random
import asyncio
import requests
from queue import Queue
from time import sleep, time
from datetime import datetime

from PIL import Image, ImageDraw, ImageFont

import discord
from discord.ext import commands

from modules.Emoji import Emoji
from modules.Smogon import Smogon
from modules.Frinkiac import Compuglobal

COMMON_PORT = os.environ['COMMON_PORT']
SMOGON_DNS = os.environ['SMOGON_DNS']

IMAGE_DIR = os.environ['IMAGE_DIR']  # for frinkiac
IMAGE_QUEUE = Queue()  # for deleting images sent from frinkiac / deepfryer

DEEPFRY_DNS = os.environ['DEEPFRY_DNS']
DEEPFRY_DIR = os.environ['DEEPFRY_DIR']


async def clearImageQueue():
    while not IMAGE_QUEUE.empty():
        print(f'clearing images...')
        os.remove(IMAGE_QUEUE.get())
        IMAGE_QUEUE.task_done()


def getRaidInfo(args):
    # TODO: This
    pass


def getFrinkiacPic(args, futurama=False):
    print((
        'Got a request for a frinkiac pic at'
        f' {datetime.now().strftime("%H:%M:%S")}'
        ),
        flush=False
    )
    sleep(0.5)  # to stop frinkiac telling me off if people are spamming

    f = Compuglobal() if not futurama \
        else Compuglobal(show='f')
    gif = True if 'g' in args or 'gif' in args \
        else False
    caption = True if 'c' in args or 'caption' in args \
        else False
    zombie = True if futurama or 'z' in args or 'zombie' in args \
        else False

    if caption and gif:
        return ''

    url, txt = f.getRandomPicURL(
        use_gif=gif,
        use_caption=caption,
        include_zombie=zombie
    )
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

    print(
        f'Got the pic at {datetime.now().strftime("%H:%M:%S")}\n',
        flush=False
    )
    IMAGE_QUEUE.put(fname)
    return fname


def writeTextToPic(path, text, futurama):
    # Decode the base64 text
    plaintext = base64.b64decode(text).decode()

    image = Image.open(path)
    size = random.randrange(30, 42, 2)
    if futurama:
        size = size * 3  # futurama pics are bigger so
        # increasing the text to compensate?
    font = ImageFont.truetype("font/AlteHaasGroteskRegular.ttf", size)
    draw = ImageDraw.Draw(image)
    x, y = [random.randint(10, 200) for i in range(2)]
    draw.text((x, y), plaintext, font=font)
    image.save(path, "JPEG")


async def getDeepfriedImage(filename):
    '''Send image to node container to deep fry it.'''
    params = {'filename': filename, 'intense': False}
    req = requests.post(
        f'http://{DEEPFRY_DNS}:{COMMON_PORT}/api/',
        params=params
    )

    # No response
    if not req.json():
        print('nothing came back from deepfrier')
        return (400, '')

    # Deepfry failed
    if req.json()['code'] == 400:
        print('got 400 from deepfrier')
        return (400, '')

    # Success
    elif req.json()['code'] == 200:
        print('success from deepfrier!')
        ret_filename = req.json()['filename']
        IMAGE_QUEUE.put(ret_filename)  # processed image
        return (200, f'{DEEPFRY_DIR}/{ret_filename}')

    # Fallback
    else:
        print('got no response but didnt get nothing either?')


async def send_message_queue(ctx, queue):
    '''Sends all `discord.Embed`s in a queue, eventually clearing it.'''
    while not queue.empty():
        await ctx.send(embed=queue.get())
        queue.task_done()


if __name__ == '__main__':
    print(r'''  ___  ____   __    __  __ _  ____  _  _
 / __)(  _ \ /  \  /  \(  / )(  __)( \/ )
( (_ \ )   /(  O )(  O ))  (  ) _)  )  /
 \___/(__\_) \__/  \__/(__\_)(____)(__/
    ''', flush=False)
    # Get token from environment variable (.env file in root dir)
    token = os.environ.get('TOKEN')
    bot = commands.Bot(command_prefix='!')

    @bot.command()
    async def hi(ctx):
        await ctx.send('hello!')

    @bot.command()
    async def wat(ctx):
        await ctx.send(embed=discord.Embed(
            description=(
                "You can send simpsons or futurama pic by typing `!s` or `!f`"
                " respectively. Use `!s gif` or `!s g` for a GIF"
                " (takes a while to send). Use `!s c` for captions."
                " The text is a random size and is placed randomly"
                " somewhere in the picture. For the simpsons, use `!s z`"
                " to include pics from zombie simpsons in the RNG."
            )
        ))

    # Smogon: moveset data
    @bot.command()
    async def smogon(ctx, *args):
        s = Smogon(SMOGON_DNS, COMMON_PORT)
        response_queue = s.get_moveset_data(args)
        await send_message_queue(ctx, response_queue)

    # Smogon: pokemon formats
    @bot.command()
    async def formats(ctx, *args):
        s = Smogon(SMOGON_DNS, COMMON_PORT)
        response_queue = s.get_formats(args)
        await send_message_queue(ctx, response_queue)

    @bot.command()
    async def s(ctx, *args):
        path = getFrinkiacPic(args)
        if not path:
            await ctx.send(embed=discord.Embed(
                description="You can't put captions on a gif yet, sorry")
            )
        else:
            await ctx.send(file=discord.File(path))
        await clearImageQueue()

    @bot.command()
    async def f(ctx, *args):
        path = getFrinkiacPic(args, futurama=True)
        if not path:
            await ctx.send(embed=discord.Embed(
                description="You can't put captions on a gif yet, sorry"
                )
            )
        else:
            await ctx.send(file=discord.File(path))
        await clearImageQueue()

    @bot.command()
    async def df(ctx, *args):
        images = ctx.message.attachments
        images = list(filter(
            lambda x: x.filename.endswith('.jpg')
            or x.filename.endswith('.png'), images)
        )

        # TODO: do url images get attached as images automatically?
        if not images:
            url = ctx.message.content.split('!df ')[1]
            if (
                re.match(r'http://|https://', url) and
                (
                    url.endswith('.jpg') or
                    url.endswith('.png')
                )
            ):
                print(f'regex matched in message')
                images.append(url)

        filenames = []
        if images:
            for img in images:
                filename = f'{time()}.jpg'
                path = f'{DEEPFRY_DIR}/{filename}'
                IMAGE_QUEUE.put(path)
                if isinstance(img, discord.Attachment):
                    await img.save(path)
                elif isinstance(img, str):
                    with open(path, 'wb') as f:
                        res = requests.get(img)
                        f.write(res.content)
                filenames.append(filename)

            for filename in filenames:
                print(f'sending {filename} to deepfrier')
                code, pic = getDeepfriedImage(filename)
                if pic:
                    print('got the new file')
                    await asyncio.wait(1)
                    await ctx.send(file=discord.File(pic))
                elif code == 400:
                    await ctx.send('something went wrong!')

            # await asyncio.sleep(2)
            clearImageQueue()
            print(f'deleted img')

    # Run the bot
    bot.run(token)
