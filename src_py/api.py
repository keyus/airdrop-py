import win32api
import win32con
import keyboard
from lib.chrome_app import Chrome_App
from lib.config import Config
from lib.app import App, chrome_process
from lib.webshare import Webshare
from lib.sync import Sync

class Api:
    def __init__(self):
        self.chrome_app = Chrome_App()
        self.config = Config()
        self.app = App()
        self.webshare = Webshare()
        self.sync = Sync()
        self._setup_hotkeys()

    def _setup_hotkeys(self):
        # 注册 Shift+S 快捷键,启用，关闭同步
        keyboard.add_hotkey('shift+s', self._toggle_sync)

    def _toggle_sync(self):
        # 切换同步状态
        print('is_sync',self.sync.is_sync,chrome_process)
        if len(chrome_process)<2:
            return 
        if self.sync.is_sync:
            self.sync.stop()
        else:
            self.sync.start()
            