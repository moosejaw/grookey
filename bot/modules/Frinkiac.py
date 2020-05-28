import re
import compuglobal

class Compuglobal:
    def __init__(self, show=None):
        self.zombie_threshold = 10 # Season denoting the zombie simpsons threshold
        self.show = compuglobal.Frinkiac()
        if show == 'f':
            self.show = compuglobal.Morbotron()

    def getScreencap(self):
        return self.show.get_random_screencap()
        

    def getRandomPicURL(self, use_gif=False, use_caption=False, include_zombie=False):
        valid = False if not include_zombie else True
        while not valid:
            sc = self.getScreencap()

            # Use GIF if specified
            if use_gif:
                sc = sc.get_gif_url()
            else:
                sc = sc.get_meme_url()

            season = re.match(r"\/S[0-9]{2}", sc).group(0)
            print(f'the match was {season} and the url was {sc}')
            season = int(season.split('/S')[1])
            
            print(f'processed season is {season} and threshold is {self.zombie_threshold}')
            if season <= self.zombie_threshold:
                valid = True
                print(f'pic ok! sending...')
            else:
                print('pic is from zombie simpsons, rerolling...')
        
        # Split the URL to remove caption
        if not use_caption:
            sc = sc.split('?')[0]
        return sc
