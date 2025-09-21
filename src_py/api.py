from lib.chrome_app import Chrome_App
from lib.config import Config
from lib.app import App
from lib.webshare import Webshare

class Api:
    def __init__(self):
        self.chrome_app = Chrome_App()
        self.config = Config()
        self.app = App()
        self.webshare = Webshare()
        
        
  