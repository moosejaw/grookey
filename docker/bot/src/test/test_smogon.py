'''Contains tests for the Smogon interfaces.'''
import os
import pytest
import discord
import asyncio
import requests
from queue import Queue
from modules.Smogon import Smogon

s = Smogon(os.environ['SMOGON_DNS'], os.environ['COMMON_PORT'])


def test_api_call_responses():
    '''
    Tests the call() function to see if the responses coming back are as
    expected. Anything that is not a 200 OK should be a discord.Embed
    describing the error. A 200 OK should return a dict containing
    the response in JSON format.
    '''
    # Expected: discord.Embed message on error, dict if successful
    param_cases = [
        {'pkmn': 'doesnotexist', 'metagame': 'ss'},  # 404 (bad pkmn)
        {'pkmn': 'mudsdale', 'metagame': 'blah'},  # 404 (bad metagame)
        {'pkmn': 'magby', 'metagame': 'gs'},  # 405 (no data yet)
        {'pkmn': 'grookey', 'metagame': 'ss'}  # OK
    ]

    for endpoint in ['movesets', 'formats']:
        for param in range(len(param_cases)):
            asyncio.set_event_loop(asyncio.new_event_loop())
            loop = asyncio.get_event_loop()

            res = loop.run_until_complete(
                s.call(param_cases[param], endpoint)
            )

            loop.close()
            if param <= 2:
                assert not isinstance(res, dict)
                assert isinstance(res, discord.Embed)

                if param <= 1:
                    assert res.title == 'Page not found!'
                else:
                    assert res.title == 'No moveset data!'
            else:
                assert isinstance(res, dict)
                assert res['code'] == 200


def test_validate_args():
    '''
    Tests the validate_args() function to check that arguments
    being used are valid for sending to the Smogon container.
    '''
    arg_cases = [
        ['grookey'],  # Not enough args
        ['ss'],  # Not enough args
        ['grookey', 'ss', 'blah'],  # Too many args
        ['grookey', 'swsh'],  # Invalid metagame (not 2 chars)
        ['grookey', 'ss'],  # OK
        ['ss', 'grookey'],  # OK
    ]
    for args in range(len(arg_cases)):
        asyncio.set_event_loop(asyncio.new_event_loop())
        loop = asyncio.get_event_loop()

        returned = loop.run_until_complete(
            s.validate_args(arg_cases[args], expected_len=2)
        )

        loop.close()

        if args <= 3:
            assert returned is not True
            assert isinstance(returned, discord.Embed)

            if args <= 2:
                assert returned.title == 'Not enough arguments!'
            else:
                assert returned.title == 'Invalid metagame argument!'

        else:
            assert returned is True


def test_parse_args():
    '''
    Tests the parse_args() function to ensure that the Pokemon and metagame
    are being extracted in the right order.
    '''
    arg_cases = [
        ['ss', 'grookey'],  # Metagame is 1st
        ['grookey', 'ss']  # Metagame is 2nd
    ]

    for args in arg_cases:
        asyncio.set_event_loop(asyncio.new_event_loop())
        loop = asyncio.get_event_loop()

        metagame, pokemon = loop.run_until_complete(
            s.parse_args(args)
        )

        loop.close()

        assert metagame == 'ss'
        assert pokemon == 'grookey'


def test_get_thumbnail_url():
    '''
    Tests the get_thumbnail_url() function to ensure that the correct
    thumbnail URLs are being returned given specific metagames.
    '''
    arg_cases = [
        ['mewtwo', 'rb'],  # Should be .png
        ['heracross', 'gs'],  # Should be .gif
        ['dragonite', 'rs'],  # Should be .png
        ['hippowdon', 'dp'],  # Should be .png
        ['druddigon', 'bw'],  # Should be .gif
        ['gallade', 'xy'],  # Should be .gif
        ['mudsdale', 'sm'],  # Should be .gif
        ['grookey', 'ss']  # Should be .gif
    ]

    for arg in arg_cases:
        asyncio.set_event_loop(asyncio.new_event_loop())
        loop = asyncio.get_event_loop()

        returned_url = loop.run_until_complete(
            s.get_thumbnail_url(arg[0], arg[1])
        )

        loop.close()

        expected_extension = '.gif'
        if arg[1] in ['rb', 'rs', 'dp']:
            expected_extension = '.png'

        assert returned_url.endswith(expected_extension)


def test_get_basestats():
    '''Tests the get_basestats function, validating arguments
    and checking the return message will send properly.

    For Gen 1, smogon still splits the 'special' stat into
    Sp Atk. and Sp Def., they just have the same value.'''
    arg_cases = [
        ['pinsir', 'rb'],  # Normal case
        ['dragapult', 'ss'],  # Normal case
        ['arceus', 'dp'],  # Poke with very high base stats
    ]

    for args in arg_cases:
        asyncio.set_event_loop(asyncio.new_event_loop())
        loop = asyncio.get_event_loop()

        output = loop.run_until_complete(
            s.get_basestats(args)
        )
        loop.close()

        # Verify
        response = output.get()
        assert len(response.description) <= 2048  # Max number of chars allowed
        for stat in [
            'HP',
            'Attack',
            'Defense',
            'Sp. Atk',
            'Sp. Def',
            'Speed'
        ]:
            assert stat in response.description
        output.task_done()


'''
The following tests ensure that the Smogon URL formats have not changed.
They aren't necessarily an indication of broken logic in the Smogon module,
but rather failure of these tests indicate that Smogon have changed their URL
syntax.
'''


def test_smogon_thumbnail_syntax():
    '''
    Tests the sprite/thumbnail URL.
    '''
    for url in [
        'https://www.smogon.com/dex/media/sprites/xy/grookey.gif',
        'https://www.smogon.com/dex/media/sprites/dp/bronzor.png'
    ]:
        r = requests.get(url)
        assert r.status_code == 200


def test_smogon_dex_syntax():
    '''
    Tests the dex URL (which points to the page containing
    moveset/format/stats info).
    '''
    for url in [
        'https://www.smogon.com/dex/xy/pokemon/abomasnow/',
        'https://www.smogon.com/dex/rb/pokemon/mewtwo/'
    ]:
        r = requests.get(url)
        assert r.status_code == 200