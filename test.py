import mouse
import win32process
import win32gui
import win32con
# 获取所有chrome
def get_parent():
    win = []
    def enum_window_callback(hwnd, windows):
        title = win32gui.GetWindowText(hwnd)
        class_name = win32gui.GetClassName(hwnd)
        win32gui.GetClassName(hwnd)
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        if class_name == 'Chrome_WidgetWin_1':
            windows.append((hwnd,pid,title, class_name))
            print(title, class_name)

    win32gui.EnumWindows(enum_window_callback, win)
    return win


def find_win(window_name):
    hwnd = win32gui.FindWindow(None, window_name)
    if hwnd > 0:
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        return (hwnd, pid)
    return None


include_title = ["扩展程序" ,"插件" ,"OKX" ,"MetaMask","钱包", "Wallet"]
exclude_title = ['- Visual Studio','- Microsoft​ Edge', 'DevTools', 'eth-', 'Google Chrome']
def get_chrome_popups(exclude_hwnd = None):
    pop = []
    def callback(hwnd, _):
        title = win32gui.GetWindowText(hwnd)
        visble = win32gui.IsWindowVisible(hwnd)
        class_name = win32gui.GetClassName(hwnd)
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        
        if visble and class_name == 'Chrome_WidgetWin_1' and not any(it in title for it in exclude_title):
            pop.append(hwnd)
            print(title,class_name, hwnd, pid)
        
    win32gui.EnumWindows(callback, None)
    return pop

# c = get_chrome_popups()

def get_pop(sync_windows=[]):
        print("get pop")
        popups = []
        pids = [win32process.GetWindowThreadProcessId(it)[1] for it in sync_windows]
        print('pids', pids)

        def callback(hwnd, _):
            title = win32gui.GetWindowText(hwnd)
            visible = win32gui.IsWindowVisible(hwnd)
            _, window_pid = win32process.GetWindowThreadProcessId(hwnd)

            if window_pid in pids and visible and not "eth-" in title:
                popups.append(hwnd)
                print(f"找到弹窗 - 句柄: {hwnd}, 标题: {title}")

        win32gui.EnumWindows(callback, None)
        return popups

# for it in c :
#     win32gui.CloseWindow(it)
# print(c)
c = get_pop([1442976])

def get_chrome_popups_by_pid(pid):
    """通过PID获取Chrome进程的弹窗句柄"""
    popups = []
    def callback(hwnd, _):
        title = win32gui.GetWindowText(hwnd)
        visible = win32gui.IsWindowVisible(hwnd)
        class_name = win32gui.GetClassName(hwnd)
        _, window_pid = win32process.GetWindowThreadProcessId(hwnd)

        if window_pid == pid and visible and class_name == 'Chrome_WidgetWin_1' and not any(it in title for it in exclude_title):
            popups.append({'hwnd': hwnd, 'title': title, 'class_name': class_name})
            print(f"找到弹窗 - 句柄: {hwnd}, 标题: {title}")

    win32gui.EnumWindows(callback, None)
    return popups


# 使用示例
# pid = 13852
# chrome_popups = get_chrome_popups_by_pid(pid)
# print(f"\n进程 {pid} 共找到 {len(chrome_popups)} 个弹窗")