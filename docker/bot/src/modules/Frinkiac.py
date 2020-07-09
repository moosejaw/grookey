import re
import compuglobal

class Compuglobal:
    def __init__(self, show=None):
        self.zombie_threshold = 10 # Season denoting the zombie simpsons threshold
        self.show = compuglobal.Frinkiac()
        if show == 'f':
            self.show = compuglobal.Morbotron()

    def roll(self, gif):
        sc = self.show.get_random_screencap()
        url = sc.get_meme_url() if not gif else sc.get_gif_url()
        return url
        

    def getRandomPicURL(self, use_gif=False, use_caption=False, include_zombie=False):
        url = ''
        valid = False
        while not valid:
            url = self.roll(use_gif)
            season = re.search(r"\/S[0-9]{2}", url).group(0)
            season = int(season.split('/S')[1])
            
            # TODO: kinda ugly, can probably be done better. it's not dry?
            if not include_zombie and season <= self.zombie_threshold:
                valid = True
            elif include_zombie and season >= self.zombie_threshold:
                valid = True
            if not valid: print('pic not valid, rerolling...', flush=False)

        print(f'pic ok!', flush=False) 
        
        # Split the URL to remove caption if needed
        url, txt = url.split('?b64lines=')
        txt = txt if use_caption else ''
        
        return (url, txt)
