import shutil
import sys
import time
import os
import psutil
from typing  import List, TypedDict, Any
from .path import user_data_path
from .config import Config
from .window.util import Util


class OpenProcess(TypedDict):
    name: str
    pid: int | None
    hwnd: Any | None

config_handle = Config()
chrome_process: List[OpenProcess] = []
telegram_process:List[OpenProcess] = []

# 程序目录
def app_path():
    if getattr(sys, "frozen", False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return base_path

def is_process_running_by_pid(pid):
    """使用psutil检查进程是否运行"""
    try:
        return psutil.pid_exists(pid)
    except:
        return False

def is_process_running_by_name_and_path(process_name, exe_path=None):
    """通过进程名和路径检查进程是否运行"""
    try:
        for proc in psutil.process_iter(['pid', 'name', 'exe']):
            if proc.info['name'] and process_name.lower() in proc.info['name'].lower():
                if exe_path is None:
                    return True
                if proc.info['exe'] and exe_path.lower() in proc.info['exe'].lower():
                    return True
        return False
    except:
        return False

class App:
    def __init__(self):
        self.util = Util()
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
            user_data_dir = os.path.join(chrome_user_data_dir, name)
            proxy = []
            if use_proxy:
                proxy_list = config_handle.get_proxy()
                if proxy_list.get('status'):
                    proxy_list = proxy_list.get('data')
                    name_index = wallet.index(name)
                    proxy_list_one = proxy_list[name_index]
                    proxy = [f"--proxy-server=socks5://{proxy_list_one}"]
            if not use_url:
                url = []
            psutil.Popen([
                chrome_path,
                f"--user-data-dir={user_data_dir}",
                f"--window-name={name}",
                "--disable-first-run-ui",
                "--no-first-run",
                "--no-default-browser-check",
                "--disable-features=TranslateUI",             #禁用翻译特性
                "--disable-features=InfiniteSessionRestore",  #禁用页面恢复弹窗提示
                "--hide-crash-restore-bubble",                #禁用页面恢复弹窗提示 windows
                *proxy,
                *url
            ])
            time.sleep(0.4)
            result = self.util.wait_chrome(name)
            chrome_process.append(
                {
                    "name": name,
                    "hwnd": result[0] if result else None,
                    "pid": result[1] if result else None,
                }
            )
        return True

    # 打开telegram
    def open_telegram(self, names: list[str]):
        config = config_handle.get_config()
        if config.get('status'):
            config = config.get('data')
        telegram_install_dir = config.get("telegram_install_dir","")
        for name in names:
            item_path = os.path.join(telegram_install_dir, name, "Telegram.exe")
            proc = psutil.Popen([item_path])
            telegram_process.append(
                {
                    "name": name,
                    "pid": proc.pid,
                }
            )
        return True

    # 关闭chrome
    def close_chrome(self, names: list[str]):
        for name in names:
            item = next((item for item in chrome_process if item['name'] == name), None)
            pid = item.get("pid")
            if pid and psutil.pid_exists(pid):
                proc = psutil.Process(pid)
                proc.kill()
                chrome_process.remove(item)
        return True

    def close_telegram(self, names: list[str]):
        for name in names:
            item = next((item for item in telegram_process if item['name'] == name), None)
            pid = item.get("pid")
            if pid and psutil.pid_exists(pid):
                proc = psutil.Process(pid)
                proc.kill()
                telegram_process.remove(item)
        return True
    
    def close_chrome_all(self):
        for item in chrome_process:
            pid = item.get("pid")
            if pid and psutil.pid_exists(pid):
                proc = psutil.Process(pid)
                proc.kill()
        chrome_process.clear()
        
    def close_telegram_all(self):
        for item in telegram_process:
            pid = item.get("pid")
            if pid and psutil.pid_exists(pid):
                proc = psutil.Process(pid)
                proc.kill()
        telegram_process.clear()

    
    def get_open(self):
        for item in chrome_process:
            pid = item.get('pid')
            if not psutil.pid_exists(pid):
                chrome_process.remove(item)
                
        for item in telegram_process:
            pid = item.get('pid')
            if not psutil.pid_exists(pid):
                telegram_process.remove(item)
        return {
            "chrome": [item.get('name') for item in chrome_process],
            "telegram": [item.get('name') for item in telegram_process],
        }

   