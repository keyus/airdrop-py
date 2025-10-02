import webview
import sys
import os
import ctypes
from dotenv import load_dotenv
load_dotenv()
from api import Api
from lib.app import App

isProduction = getattr(sys, "frozen", False)
def is_admin():
    # 检查是否具有管理员权限
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    # 以管理员权限重新运行程序
    try:
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit(0)  # 退出当前进程
    except Exception as e:
        print(f"无法获取管理员权限: {e}")
        return False

def get_ui_path():
    if isProduction:
        # 获取PyInstaller临时目录路径
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_path, 'dist', 'index.html')
    else:
        return "http://localhost:3000/"

ui = get_ui_path()

def create_window():
    window = webview.create_window(
        "Airdrop",
        ui,
        js_api=Api(),
        width=1000,
        height=820,
        resizable=True,
        min_size=(1000, 820),
    )
    return window

if __name__ == "__main__":
    if is_admin():
        App().init()
        window = create_window()
        webview.start(debug=not isProduction)
    else:
        print("正在请求管理员权限...")
        if run_as_admin() == False:
            print("需要管理员权限才能运行此程序")
            input("按任意键退出...")
            sys.exit(1)
    