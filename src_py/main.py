import webview
import sys
from api import Api
from lib.app import App

isProduction = getattr(sys, "frozen", False)
ui = '../dist/index.html' if isProduction else "http://localhost:3000/"

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