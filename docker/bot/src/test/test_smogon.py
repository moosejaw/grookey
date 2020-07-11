'''Contains tests for the Smogon interfaces.'''
import os
import pytest
import discord
from modules.Smogon import Smogon

s = Smogon(os.envrion['SMOGON_DNS'], os.environ['COMMON_PORT'])


# General data retrieval tests
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
            res = await s.call(param_cases[param], endpoint)

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
        ['grookey']  # Not enough args
        ['ss']  # Not enough args
        ['grookey', 'ss', 'blah']  # Too many args
        ['grookey', 'swsh']  # Invalid metagame (not 2 chars)
        ['grookey', 'ss']  # OK
        ['ss', 'grookey']  # OK
    ]
    for args in range(len(arg_cases)):
        returned = await s.validate_args(args, expected_len=2)

        if args <= 3:
            assert returned is not True
            assert isinstance(returned, discord.Embed)

            if args <= 2:
                assert returned.title == 'Not enough arguments!'
            else:
                assert returned.title == 'Invalid metagame argument!'

        else:
            assert returned is True
