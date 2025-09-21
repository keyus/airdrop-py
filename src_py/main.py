import webview
import sys
import os
from api import Api
from lib.app import App

isProduction = getattr(sys, "frozen", False)

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
    App().init()
    window = create_window()
    webview.start(debug=not isProduction)