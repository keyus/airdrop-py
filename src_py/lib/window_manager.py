import ctypes
import win32gui
import win32con
import win32process
from typing import List, Tuple

def get_wininfo():
    user32 = ctypes.windll.user32
    user32.SetProcessDPIAware()
    # 获取屏幕尺寸
    screen_width = user32.GetSystemMetrics(0)  # SM_CXSCREEN
    screen_height = user32.GetSystemMetrics(1)  # SM_CYSCREEN
    # 获取主显示器的DPI
    hdc = user32.GetDC(0)
    dpi_x = ctypes.windll.gdi32.GetDeviceCaps(hdc, 88)  # LOGPIXELSX
    user32.ReleaseDC(0, hdc)
    # 标准DPI是96，计算缩放比例
    scale = dpi_x / 96.0
    chrome_height = screen_height - 100
    chrome_width = 750
    return {
        "user32": user32,
        "screen_width": screen_width,
        "screen_height": screen_height,
        "chrome_height": chrome_height,
        "chrome_width": chrome_width,
        "scale": scale,
    }

config = get_wininfo()

class WindowManager:
    def get_chrome_windows(self, pids: List[int]) -> List[Tuple[int, int]]:
        chrome_windows = {
            "main": [],
            "children": [],
        }
        def enum_callback(hwnd, windows):
            try:
                _, win_pid = win32process.GetWindowThreadProcessId(hwnd)
                if win_pid in pids:
                    title = win32gui.GetWindowText(hwnd)
                    class_name = win32gui.GetClassName(hwnd)
                    if class_name == "Chrome_WidgetWin_1":
                        if title.endswith('- Google Chrome'):
                            windows['main'].append((hwnd,win_pid))
                        else:
                            windows['children'].append((hwnd,win_pid))
            except:
                pass
            return True

        win32gui.EnumWindows(enum_callback, chrome_windows)
        return chrome_windows

    
    def set_window_pos(self,hwnd, x=None, y=None, width=None, height=None, topmost=None, show=True):
        """
        通用窗口控制函数：可移动、调整大小、置顶、显示/隐藏窗口
        """
        # 获取当前窗口位置和大小
        current_rect = win32gui.GetWindowRect(hwnd)
        current_x, current_y = current_rect[0], current_rect[1]
        current_width = current_rect[2] - current_rect[0]
        current_height = current_rect[3] - current_rect[1]

        # 使用当前值如果参数为None
        final_x = x if x is not None else current_x
        final_y = y if y is not None else current_y
        final_width = width if width is not None else current_width
        final_height = height if height is not None else current_height

        # 设置Z序
        if topmost is True:
            insert_after = win32con.HWND_TOPMOST
        elif topmost is False:
            insert_after = win32con.HWND_NOTOPMOST
        else:
            insert_after = win32con.HWND_NOTOPMOST  # 确保窗口不会置顶

        # 设置标志
        flags = win32con.SWP_SHOWWINDOW if show else win32con.SWP_HIDEWINDOW

        # 调用 WinAPI
        result = win32gui.SetWindowPos(hwnd, insert_after, final_x, final_y, final_width, final_height, flags)
        return result

    def windows_horizontal(self, pids) -> dict:
        windows = self.get_chrome_windows(pids)
        main = windows.get('main')
        if len(main) < 1:
            return {"success": False, "error": "未找到Chrome窗口"}
        
        def sort():
            # 排列窗口
            for i, (hwnd,_) in enumerate(main):
                # 计算位置
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                width = config.get('chrome_width')
                height = config.get('chrome_height')
                x = i * config.get('chrome_width')
                self.set_window_pos(hwnd=hwnd, x= x, y= 0, width=width, height=height)
        sort()
        sort()  #两次调用,防止最小化、隐藏
        return {"success": True, "message": f"成功排列"}

   