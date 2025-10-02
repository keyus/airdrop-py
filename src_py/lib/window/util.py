import ctypes
import keyboard
import win32gui
import win32process
import win32con
import win32api
import time
import mouse
from typing import List


# 获取屏幕宽度和高度
ctypes.windll.shcore.SetProcessDpiAwareness(2)
screen_width = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
screen_height = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
chrome_height = screen_height - 100  # chrome窗口预设排列高
chrome_width = 750  # chrome窗口预设排列宽
move_interval = 0.03  # 鼠标移动节流阀
mouse_threshold = 3  # 鼠标移动距离节流阀
last_move_time = 0  # 鼠标最后移动时间
last_mouse_position = (0, 0)  # 鼠标最后停留的位置
last_key_time = 0  # 监听最后按压时间
last_key = None  # 最后按下的键

# 需要排除的chrome弹窗名，弱匹配
exclude_title = [
    "- Visual Studio",
    "- Google Chrome",
    "- Microsoft​ Edge",
]
# 普通按键
normal_key = [
    "enter",
    "backspace",
    "tab",
    "esc",
    "space",
    "up",
    "down",
    "left",
    "right",
    "home",
    "end",
    "page up",
    "page down",
    "delete",
    "f1",
    "f2",
    "f3",
    "f4",
    "f5",
    "f6",
    "f7",
    "f8",
    "f9",
    "f10",
    "f11",
    "f12",
]
# windows vk map
vk_map = {
    "enter": win32con.VK_RETURN,
    "backspace": win32con.VK_BACK,
    "tab": win32con.VK_TAB,
    "esc": win32con.VK_ESCAPE,
    "space": win32con.VK_SPACE,
    "up": win32con.VK_UP,
    "down": win32con.VK_DOWN,
    "left": win32con.VK_LEFT,
    "right": win32con.VK_RIGHT,
    "home": win32con.VK_HOME,
    "end": win32con.VK_END,
    "page up": win32con.VK_PRIOR,
    "page down": win32con.VK_NEXT,
    "delete": win32con.VK_DELETE,
    "f1": win32con.VK_F1,
    "f2": win32con.VK_F2,
    "f3": win32con.VK_F3,
    "f4": win32con.VK_F4,
    "f5": win32con.VK_F5,
    "f6": win32con.VK_F6,
    "f7": win32con.VK_F7,
    "f8": win32con.VK_F8,
    "f9": win32con.VK_F9,
    "f10": win32con.VK_F10,
    "f11": win32con.VK_F11,
    "f12": win32con.VK_F12,
}


class Util:
    def reset_const(self):
        global move_interval
        global mouse_threshold
        global last_move_time
        global last_mouse_position
        global last_key_time
        global last_key
        move_interval = 0.01
        mouse_threshold = 2
        last_move_time = 0
        last_mouse_position = (0, 0)
        last_key_time = 0
        last_key = None

    # 是否是chrome 窗口类型,包启弹窗，插件
    def is_chrome_window(self, hwnd: int) -> bool:
        title = win32gui.GetWindowText(hwnd)
        class_name = win32gui.GetClassName(hwnd)
        if class_name == "Chrome_WidgetWin_1" and not any(
            it in title for it in exclude_title
        ):
            return True
        return False

    # 枚举chrome所有弹窗
    def get_pop(self, sync_windows: List[int] = []) -> List[int]:
        popups = []
        pids = [win32process.GetWindowThreadProcessId(it)[1] for it in sync_windows]

        def callback(hwnd, _):
            title = win32gui.GetWindowText(hwnd)
            visible = win32gui.IsWindowVisible(hwnd)
            _, window_pid = win32process.GetWindowThreadProcessId(hwnd)

            if window_pid in pids and visible and not "eth-" in title:
                popups.append(hwnd)
                # print(f"找到弹窗 - 句柄: {hwnd}, 标题: {title}")

        win32gui.EnumWindows(callback, None)
        return popups

    # 根据钱包名称，获取对应的窗口
    def get_chrome_window(self, window_name: str) -> tuple[int, int]:
        hwnd = win32gui.FindWindow(None, window_name)
        if hwnd > 0:
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            return (hwnd, pid)
        return None

    # 设置窗口大小，位置 index:索引 补x位置
    def set_position(self, hwnd: int, index: int = 0):
        x = chrome_width * index
        try:
            # 先显示窗口
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            time.sleep(0.2)
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            time.sleep(0.2)
            # 设置窗口位置
            win32gui.SetWindowPos(
                hwnd,
                win32con.HWND_TOP,
                x,
                0,
                chrome_width,
                chrome_height,
                win32con.SWP_SHOWWINDOW,
            )
        except Exception as e:
            print(f"设置窗口位置失败: {e}")

    # 等待chrome启动完成
    def wait_chrome(self, name: str, max_wait_time=10, check_interval=0.1):
        """等待Chrome窗口启动完成"""
        start_time = time.time()
        while time.time() - start_time < max_wait_time:
            find = self.get_chrome_window(name)
            if find:
                return find
            time.sleep(check_interval)
        return None

    # 同步操作到目标window  event:事件, target_hwnd:目标窗口句柄  event_rel_point:事件源窗口的相当坐标
    def sync_hwnd(
        self, event, target_hwnd: int, event_rel_point: tuple[int, int] = (0, 0)
    ):
        try:
            # 获取目标窗口尺寸
            left,top,right,bottom = win32gui.GetWindowRect(target_hwnd)
            # 计算目标坐标
            client_x = int((right - left) * event_rel_point[0])
            client_y = int((bottom - top) * event_rel_point[1])
            # print('target_hwnd',target_hwnd, client_x, client_y)
            lparam = win32api.MAKELONG(client_x, client_y)
            # 处理滚轮事件
            if isinstance(event, mouse.WheelEvent):
                self.mouse_wheel(event, target_hwnd)
            # 处理鼠标点击
            elif isinstance(event, mouse.ButtonEvent):
                self.mouse_press(event, target_hwnd, lparam)
            # 处理鼠标移动
            elif isinstance(event, mouse.MoveEvent):
                self.move(event, target_hwnd, lparam)

        except Exception as e:
            pass

    # 目标窗口鼠标移动
    def move(self, hwnd: int, lparam):
        win32gui.PostMessage(hwnd, win32con.WM_MOUSEMOVE, 0, lparam)

    # 目标窗口鼠标点击
    def mouse_press(
        self,
        event: mouse.ButtonEvent,
        hwnd: int,
        lparam,
    ):
        if event.event_type == mouse.DOWN:
            if event.button == mouse.LEFT:
                return win32gui.PostMessage(
                    hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lparam
                )
            if event.button == mouse.RIGHT:
                return win32gui.PostMessage(
                    hwnd, win32con.WM_RBUTTONDOWN, win32con.MK_RBUTTON, lparam
                )
        if event.event_type == mouse.UP:
            if event.button == mouse.LEFT:
                return win32gui.PostMessage(hwnd, win32con.WM_LBUTTONUP, 0, lparam)
            if event.button == mouse.RIGHT:
                return win32gui.PostMessage(hwnd, win32con.WM_RBUTTONUP, 0, lparam)

    # 鼠标滚动
    def mouse_wheel(self, event: mouse.WheelEvent, hwnd: int):
        wheel_delta = int(event.delta)
        # 获取滚轮方向和绝对值
        abs_delta = abs(wheel_delta)
        scroll_up = wheel_delta > 0
        try:
            # 根据滚动大小决定策略，微调使同步窗口滚动幅度更接近主窗口
            if abs_delta <= 1:
                # 对于小幅度滚动，减少到2次箭头键
                vk_code = win32con.VK_UP if scroll_up else win32con.VK_DOWN
                for _ in range(2):
                    win32gui.PostMessage(hwnd, win32con.WM_KEYDOWN, vk_code, 0)
                    win32gui.PostMessage(hwnd, win32con.WM_KEYUP, vk_code, 0)
            elif abs_delta <= 3:
                # 对于中等幅度滚动，使用一次Page键但减少额外的箭头键
                page_vk = (
                    win32con.VK_PRIOR if scroll_up else win32con.VK_NEXT
                )  # Page Up/Down
                win32gui.PostMessage(hwnd, win32con.WM_KEYDOWN, page_vk, 0)
                win32gui.PostMessage(hwnd, win32con.WM_KEYUP, page_vk, 0)

                # 额外只增加1次箭头键，减少之前的额外按键
                vk_code = win32con.VK_UP if scroll_up else win32con.VK_DOWN
                win32gui.PostMessage(hwnd, win32con.WM_KEYDOWN, vk_code, 0)
                win32gui.PostMessage(hwnd, win32con.WM_KEYUP, vk_code, 0)
            else:
                # 对于大幅度滚动，减少Page键系数
                page_count = min(
                    int(abs_delta * 0.4), 2
                )  # 系数从0.6降到0.4，最多减少到2次
                page_vk = win32con.VK_PRIOR if scroll_up else win32con.VK_NEXT

                for _ in range(page_count):
                    win32gui.PostMessage(hwnd, win32con.WM_KEYDOWN, page_vk, 0)
                    win32gui.PostMessage(hwnd, win32con.WM_KEYUP, page_vk, 0)

                # 移除额外的箭头键调整
        except Exception as e:
            print(f"处理滚轮事件失败: {str(e)}")

    # 鼠标移动事件节流
    def mouse_throttling(self, event: mouse.MoveEvent):
        global move_interval
        global mouse_threshold
        global last_mouse_position
        global last_move_time
        current_time = time.time()
        # 时间节流：忽略过于频繁的移动事件
        if current_time - last_move_time < move_interval:
            return False
        # 距离节流：忽略过小的移动
        dx = abs(event.x - last_mouse_position[0])
        dy = abs(event.y - last_mouse_position[1])
        if dx < mouse_threshold and dy < mouse_threshold:
            return False
        # 更新上次位置和时间
        last_mouse_position = (event.x, event.y)
        last_move_time = current_time
        return True

    # 键盘事件节流
    def keyboard_throttling(self, event: keyboard.KeyboardEvent):
        global last_key_time
        global last_key
        current_time = time.time()
        if last_key_time == 0 or current_time - last_key_time > 0.01:
            last_key_time = current_time
        else:
            if last_key == event.name and event.event_type == keyboard.KEY_DOWN:
                return False
        last_key = event.name
        return True

    # 键盘操作
    def keyboard_press(self, event: keyboard.KeyboardEvent, hwnd: int):
        modifiers = 0
        try:
            # 检测组合键状态
            modifier_keys = {
                "ctrl": {
                    "pressed": keyboard.is_pressed("ctrl"),
                    "vk": win32con.VK_CONTROL,
                    "flag": win32con.MOD_CONTROL,
                },
                "alt": {
                    "pressed": keyboard.is_pressed("alt"),
                    "vk": win32con.VK_MENU,
                    "flag": win32con.MOD_ALT,
                },
                "shift": {
                    "pressed": keyboard.is_pressed("shift"),
                    "vk": win32con.VK_SHIFT,
                    "flag": win32con.MOD_SHIFT,
                },
            }

            # 处理修饰键和组合键
            for mod_name, mod_info in modifier_keys.items():
                if mod_info["pressed"]:
                    # 按下修饰键
                    if event.event_type == keyboard.KEY_DOWN:
                        win32gui.PostMessage(
                            hwnd, win32con.WM_KEYDOWN, mod_info["vk"], 0
                        )

                    modifiers |= mod_info["flag"]

            # 处理 Ctrl+组合键的特殊情况
            if modifier_keys["ctrl"]["pressed"] and event.name in [
                "a",
                "c",
                "v",
                "x",
                "z",
            ]:
                vk_code = ord(event.name.upper())
                if event.event_type == keyboard.KEY_DOWN:
                    # 发送组合键序列
                    win32gui.PostMessage(hwnd, win32con.WM_KEYDOWN, vk_code, 0)
                    win32gui.PostMessage(hwnd, win32con.WM_KEYUP, vk_code, 0)
                return

            # 处理普通按键
            if event.name in normal_key:
                vk_code = vk_map[event.name]
                # 发送按键消息
                if event.event_type == keyboard.KEY_DOWN:
                    win32gui.PostMessage(hwnd, win32con.WM_KEYDOWN, vk_code, 0)
                else:
                    win32gui.PostMessage(hwnd, win32con.WM_KEYUP, vk_code, 0)
            else:
                # 处理普通字符
                if len(event.name) == 1:
                    vk_code = win32api.VkKeyScan(event.name[0]) & 0xFF
                    if event.event_type == keyboard.KEY_DOWN:
                        # 直接发送字符消息，更有效
                        win32gui.PostMessage(
                            hwnd, win32con.WM_CHAR, ord(event.name[0]), 0
                        )
                return

            # 释放修饰键 - 仅在按键弹起时释放
            if event.event_type == keyboard.KEY_UP:
                for mod_name, mod_info in modifier_keys.items():
                    if mod_info["pressed"]:
                        win32gui.PostMessage(hwnd, win32con.WM_KEYUP, mod_info["vk"], 0)

        except Exception as e:
            print(f"同步键盘事件到窗口 {hwnd} 失败: {str(e)}")

    # 获取鼠标坐标在窗口的位置系数0.1-1 mouse_pos:电脑鼠标坐标 窗口矩形rect区域 win32gui.GetWindowRect(self.master_window)
    def get_pos_in_window(
        self,
        mouse_pos: tuple[
            int,
            int,
        ],
        window_rect: tuple[int, int, int, int],
    ) -> tuple[int, int]:
        left, top, right, bottom = window_rect
        x, y = mouse_pos
        rel_x = (x - left) / max((right - left), 1)
        rel_y = (y - top) / max((bottom - top), 1)
        return (rel_x, rel_y)

    # 鼠标位置是否在目标窗口
    def is_pos_in_window(
        self,
        mouse_pos: tuple[
            int,
            int,
        ],
        window_rect: tuple[int, int, int, int],
    ) -> bool:
        left, top, right, bottom = window_rect
        x, y = mouse_pos
        return x >= left and x <= right and y >= top and y <= bottom
