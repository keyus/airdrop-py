import subprocess
import psutil
import shutil
import sys
import os
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
            debugging_port = 9222 + name_index
            if proxy:
                proxy = [f"--proxy-server=socks5://{proxy}"]
            if not use_url:
                url = []
            if not use_proxy:
                proxy = []
            process = subprocess.Popen(
                [
                    chrome_path, 
                    f"--user-data-dir={os.path.join(chrome_user_data_dir, name)}",
                    f"--remote-debugging-port={debugging_port}",
                    "--remote-allow-origins=*",
                    *proxy,
                    *url,
                ]
            )
            chrome_process.append(
                {
                    "name": name,
                    "pid": process.pid,
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
            process = subprocess.Popen([item_path])
            telegram_process.append(
                {
                    "name": name,
                    "pid": process.pid,
                }
            )
        return True

    def close_chrome(self, names: list[str]):
        for name in names:
            process = next((item for item in chrome_process if item['name'] == name), None)
            print("需要关闭的chrome进程", process["pid"])
            proc = psutil.Process(process["pid"])
            proc.kill()
            chrome_process.remove(process)
        return True

    def close_telegram(self, names: list[str]):
        for name in names:
            item = next((item for item in telegram_process if item['name'] == name), None)
            print("需要关闭的telegram进程", item["pid"])
            proc = psutil.Process(item["pid"])
            proc.kill()
            telegram_process.remove(item)
        return True
    
    def close_chrome_all(self):
        for item in chrome_process:
            pid = item.get('pid')
            try:
                proc = psutil.Process(pid)
                proc.kill()
            except psutil.NoSuchProcess:
                print(f"进程 {pid} 已不存在")
        chrome_process.clear()
        
    def close_telegram_all(self):
        for item in telegram_process:
            pid = item.get('pid')
            try:
                proc = psutil.Process(pid)
                proc.kill()
            except psutil.NoSuchProcess:
                print(f"进程 {pid} 已不存在")
            except psutil.AccessDenied:
                print(f"没有权限关闭进程 {pid}")
        telegram_process.clear()

    def get_open(self):
        pids = psutil.pids()
        for item in chrome_process:
            if not item["pid"] in pids:
                chrome_process.remove(item)

        for item in telegram_process:
            if not item["pid"] in pids:
                telegram_process.remove(item)
        return {
            "chrome": chrome_process,
            "telegram": telegram_process,
        }


  