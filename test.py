import ctypes
from typing import List, Tuple
import win32gui
import win32process
import win32con
import time


# 定义常量
SWP_NOSIZE = 0x0001
SWP_NOMOVE = 0x0002
SWP_NOZORDER = 0x0004
SWP_NOREDRAW = 0x0008
SWP_NOACTIVATE = 0x0010
SWP_FRAMECHANGED = 0x0020
SWP_SHOWWINDOW = 0x0040
SWP_HIDEWINDOW = 0x0080

HWND_TOPMOST = -1
HWND_NOTOPMOST = -2
HWND_TOP = 0
HWND_BOTTOM = 1

pids = [18340,22544,21344]
def get_chrome_windows(pids: List[int]) -> List[Tuple[int, int]]:
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
                            print('title', title)
                            windows['main'].append((hwnd,win_pid))
                        else:
                            windows['children'].append((hwnd,win_pid))
            except:
                pass
            return True

        win32gui.EnumWindows(enum_callback, chrome_windows)
        return chrome_windows
    
result = get_chrome_windows(pids)

print('result', result)

def set_window_pos(hwnd, x=None, y=None, width=None, height=None, topmost=None, show=True):
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
        insert_after = HWND_TOPMOST
    elif topmost is False:
        insert_after = HWND_NOTOPMOST
    else:
        insert_after = HWND_NOTOPMOST  # 确保窗口不会置顶

    # 设置标志
    flags = SWP_SHOWWINDOW if show else SWP_HIDEWINDOW

    # 调用 WinAPI
    result = win32gui.SetWindowPos(hwnd, insert_after, final_x, final_y, final_width, final_height, flags)
    print(f"SetWindowPos({hwnd}, {insert_after}, {final_x}, {final_y}, {final_width}, {final_height}, {flags}) = {result}")
    return result




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
        "chrome_height": int(chrome_height),
        "chrome_width": int(chrome_width),
        "scale": scale,
    }

config = get_wininfo()


def test ():
    # 排列窗口
    for i, (hwnd,_) in enumerate(result.get('main')):
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        width = config.get('chrome_width')
        height = config.get('chrome_height')
        x = i * config.get('chrome_width')
        result_code = set_window_pos(hwnd=hwnd, x= x, y= 0, width=width, height=height,)
test()
test()