import compuglobal

class Compuglobal:
    def __init__(self, show=None):
        self.show = compuglobal.Frinkiac()
        if show == 'f':
            self.show = compuglobal.Morbotron()
        

    def getRandomPicURL(self, use_gif=False, use_caption=False):
        sc = self.show.get_random_screencap()

        # Use GIF if specified
        if use_gif:
            sc = sc.get_gif_url()
        else:
            sc = sc.get_meme_url()
        
        # Split the URL to remove caption
        if not use_caption:
            sc = sc.split('?')[0]
        return sc
