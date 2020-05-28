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
        sc = self.getScreencap()
        url = sc.get_meme_url() if not use_gif else sc.get_gif_url()
        valid = False if not include_zombie else True
        while not valid:
            season = re.search(r"\/S[0-9]{2}", url).group(0)
            print(f'the match was {season} and the url was {url}', flush=False)
            season = int(season.split('/S')[1])
            
            print(f'processed season is {season} and threshold is {self.zombie_threshold}', flush=False)
            if season <= self.zombie_threshold:
                valid = True
                print(f'pic ok! sending...')
            else:
                sc = self.getScreencap()
                url = sc.get_meme_url()
                print('pic is from zombie simpsons, rerolling...', flush=False)
        
        # Split the URL to remove caption
        if not use_caption:
            url = url.split('?')[0]
        return url
