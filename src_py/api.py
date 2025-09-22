from lib.chrome_app import Chrome_App
from lib.config import Config
from lib.app import App
from lib.webshare import Webshare
from lib.sync import Sync

class Api:
    def __init__(self):
        self.chrome_app = Chrome_App()
        self.config = Config()
        self.app = App()
        self.webshare = Webshare()
        self.sync = Sync()

    # Chrome群控API - 极简接口
    def sync_start(self):
        """一键启动Chrome群控服务 - 自动将chrome_process[0]设为主控，其他为被控"""
        return self.sync.start()
