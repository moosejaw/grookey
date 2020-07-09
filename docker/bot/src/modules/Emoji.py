# This is completely broken and needs sorting out...
# TODO: this

class Emoji:
    '''Contains the emoji lookups and convenient functions
    for returning messages.'''
    def __init__(self):
        self.emojis = \
        {
            'grookey': r'<a:grookey:675858815148752906>',
            'koffing': r'<a:koffing:675860676836720640>'
        }

    def appendEmoji(self, emoji, msg, prepend=False):
        '''Appends an emoji to a given input string.'''
        if prepend: 
            return f'{self.emojis[emoji]} {msg}'
        return f'{msg} {self.emojis[emoji]}'
