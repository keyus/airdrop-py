from pywinauto.win32functions import GetSystemMetrics
import time

screen_width = GetSystemMetrics(0)   # SM_CXSCREEN
screen_height = GetSystemMetrics(1)  # SM_CYSCREEN
chrome_height = screen_height - 100
chrome_width = 750

class Tools:
    def __init__(self, app, index):
        self.index = index
        self.app = app
        self.chrome_window = self.get_main_window()
    def get_main_window(self,):
        windows = self.app.windows()
        chrome_window = None
        for win in windows:
            try:
                title = win.window_text()
                class_name = win.class_name()
                # 找到Chrome主窗口（通常标题包含"Google Chrome"且类名是"Chrome_WidgetWin_1"）
                if title.endswith('- Google Chrome') and class_name == "Chrome_WidgetWin_1":
                    chrome_window = win
                    break
            except:
                continue
        return chrome_window
    
    # 调用2次
    def set_win_pos(self):
        max = 2
        while max > 0:
            self.chrome_window.restore()
            time.sleep(0.1)
            x = self.index * chrome_width
            y = 0
            self.chrome_window.move_window(x, y, chrome_width, chrome_height)
            max -= 1