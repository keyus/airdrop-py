import shutil
import sys
import os
import time
import pywinauto
from .path import user_data_path
from .config import Config

config_handle = Config()
chrome_process = []
telegram_process = []

# 程序目录
def app_path():
    if getattr(sys, "frozen", False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return base_path

class App:
    
    def init(self):
        app_config_path = os.path.join(app_path(),"config")
        if not os.path.exists(user_data_path):
            shutil.copytree(app_config_path, user_data_path)


    def clear(self):
        app_config_path = os.path.join(app_path(),"config")
        if os.path.exists(user_data_path):
            shutil.rmtree(user_data_path)
        shutil.copytree(app_config_path, user_data_path)
    
    # 打开chrome
    def open_chrome(self, names: list[str]):
        config = config_handle.get_config()
        if config.get('status'):
            config = config.get('data')
        url = config.get("url", [])
        use_url = config.get("use_url", False)
        use_proxy = config.get("use_proxy", False)
        chrome_install_dir= config.get("chrome_install_dir", "")
        chrome_user_data_dir = config.get("chrome_user_data_dir", "")
        wallet = config.get("wallet",[])
        chrome_path = os.path.join(chrome_install_dir, "chrome.exe")

        for name in names:
            proxy_list = config_handle.get_proxy()
            if proxy_list.get('status'):
                proxy_list = proxy_list.get('data')
            name_index = wallet.index(name)
            proxy = proxy_list[name_index]
            if proxy:
                proxy = [f"--proxy-server=socks5://{proxy}"]
            if not use_url:
                url = []
            if not use_proxy:
                proxy = []

            user_data_path = os.path.join(chrome_user_data_dir, name)

            app = pywinauto.Application()
            cmd_args = [f"--user-data-dir={user_data_path}", *proxy, *url]
            cmd_line = f"{chrome_path} {' '.join(cmd_args)}"
            app.start(cmd_line=cmd_line)
            chrome_process.append(
                {
                    "app": app,
                    "name": name,
                }
            )
            time.sleep(0.2)
        return True

    # 打开telegram
    def open_telegram(self, names: list[str]):
        config = config_handle.get_config()
        if config.get('status'):
            config = config.get('data')
        telegram_install_dir = config.get("telegram_install_dir","")
        for name in names:
            item_path = os.path.join(telegram_install_dir, name, "Telegram.exe")
            app = pywinauto.Application()
            app.start(item_path)
            telegram_process.append(
                {
                    "app": app,
                    "name": name,
                }
            )
        return True

    def close_chrome(self, names: list[str]):
        for name in names:
            item = next((item for item in chrome_process if item['name'] == name), None)
            app = item.get('app')
            app.kill()
            chrome_process.remove(item)
        return True

    def close_telegram(self, names: list[str]):
        for name in names:
            item = next((item for item in telegram_process if item['name'] == name), None)
            app = item.get('app')
            app.kill()
            telegram_process.remove(item)
        return True
    
    def close_chrome_all(self):
        for item in chrome_process:
            app = item.get('app')
            app.kill()
        chrome_process.clear()
        
    def close_telegram_all(self):
        for item in telegram_process:
            app = item.get('app')
            app.kill()
        telegram_process.clear()

    
    def get_open(self):
        for item in chrome_process:
            chrome_app = item.get('app')
            if not chrome_app.is_process_running():
                chrome_process.remove(item)
        
        for item in telegram_process:
            telegram_app = item.get('app')
            if not telegram_app.is_process_running():
                telegram_process.remove(item)
        
        return {
            "chrome": [item.get('name') for item in chrome_process],
            "telegram": [item.get('name') for item in telegram_process],
        }

   