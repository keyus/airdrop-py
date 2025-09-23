import win32gui
import win32process
import win32con
import win32api
import ctypes
from ctypes import wintypes
import threading
import time
import sys
import keyboard
import mouse
import traceback

# 添加滚轮钩子所需的结构体定义
class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

class MSLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [
        ("pt", POINT),
        ("mouseData", wintypes.DWORD),
        ("flags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.POINTER(wintypes.ULONG))
    ]

def is_admin():
    # 检查是否具有管理员权限
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    # 以管理员权限重新运行程序
    pass
    # ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)

class ChromeManager:
    def __init__(self):
        """初始化"""
        # 记录启动时间用于性能分析
        self.start_time = time.time()
        
        # 默认设置值
        self.show_chrome_tip = True  # 是否显示Chrome后台运行提示
        
        # 加载设置
        self.settings = self.load_settings()
        
        self.enable_cdp = True  # 始终开启CDP
        # 从设置中读取是否显示Chrome提示的设置
        if 'show_chrome_tip' in self.settings:
            self.show_chrome_tip = self.settings['show_chrome_tip']
        
        # 滚轮钩子相关参数
        self.wheel_hook_id = None
        self.wheel_hook_proc = None
        self.standard_wheel_delta = 120  # 标准滚轮增量值
        self.last_wheel_time = 0
        self.wheel_threshold = 0.05  # 秒，防止事件触发过于频繁
        self.use_wheel_hook = True  # 是否使用滚轮钩子
        # 存储快捷方式编号和进程ID的映射关系
        self.shortcut_to_pid = {}
        # 存储进程ID和窗口编号的映射关系
        self.pid_to_number = {}
        if not is_admin():
            print('权限不足，正在尝试以管理员权限重新运行程序...')
            run_as_admin()
                
        self.window_list = None
        self.windows = []
        self.master_window = None
        self.screens = []  # 初始化屏幕列表
        
        self.path_entry = None
        
        self.is_syncinging = False
        self.mouse_hook_id = None
        self.keyboard_hook = None
        self.hook_thread = None
        self.user32 = ctypes.WinDLL('user32', use_last_error=True)
        self.sync_windows = []
        self.chrome_drivers = {}
        self.popup_mappings = {}
        self.popup_monitor_thread = None
        self.mouse_threshold = 3
        self.last_mouse_position = (0, 0)
        self.last_move_time = 0
        self.move_interval = 0.016
        
  

    def set_master_window(self, hwnd: int):
        """设置主控窗口"""
        try:
            # 如果正在同步，先停止同步
            if self.is_syncinging:
                self.stop_sync()
                self.is_syncinging = False

            # 设置新的主控窗口
            self.master_window = hwnd
            print(f"设置主控窗口: {hwnd}")

        except Exception as e:
            print(f"设置主控窗口失败: {str(e)}")

    def add_sync_window(self, hwnd: int, window_num: int = None):
        """添加被控窗口"""
        try:
            if hwnd not in self.sync_windows:
                self.sync_windows.append(hwnd)
                print(f"添加同步窗口: {hwnd} (编号: {window_num})")
        except Exception as e:
            print(f"添加同步窗口失败: {str(e)}")

    def start_sync(self):
        """开始同步"""
        try:
            # 确保主控窗口存在
            if not self.master_window:
                raise Exception("未设置主控窗口")
            
            # 清除之前可能的同步状态
            if hasattr(self, 'is_syncing') and self.is_syncinging:
                self.stop_sync()
                time.sleep(0.2)  # 等待资源清理

            # 初始化同步状态变量
            self.is_syncinging = True
            self.popup_windows = []  # 储存所有弹出窗口
            self.last_mouse_position = (0, 0)
            self.last_move_time = time.time()
            
            # 初始化弹出窗口列表（已在add_sync_window中添加）
            print(f"当前同步窗口: {self.sync_windows}")
            print(f"主控窗口: {self.master_window}")
            
            # 启动键盘和鼠标钩子
            if not hasattr(self, 'hook_thread') or not self.hook_thread or not self.hook_thread.is_alive():
                self.hook_thread = threading.Thread(target=self.message_loop)
                self.hook_thread.daemon = True
                self.hook_thread.start()
                
                try:
                    # 设置键盘和鼠标钩子
                    keyboard.hook(self.on_keyboard_event)
                    mouse.hook(self.on_mouse_event)
                    print("已设置键盘和鼠标钩子")
                    
                    # 尝试安装低级滚轮钩子，但不强制要求成功
                    if self.use_wheel_hook:
                        try:
                            self.setup_wheel_hook()
                            print("已安装低级滚轮钩子")
                        except Exception as e:
                            print(f"安装低级滚轮钩子失败: {str(e)}")
                            print("将使用常规鼠标钩子代替低级滚轮钩子")
                            # 失败后设置为不使用低级钩子
                            self.use_wheel_hook = False
                except Exception as e:
                    print(f"设置钩子失败: {str(e)}")
                    self.stop_sync()
                    raise Exception(f"无法设置输入钩子: {str(e)}")
                
                # 启动插件窗口监控线程
                self.popup_monitor_thread = threading.Thread(target=self.monitor_popups)
                self.popup_monitor_thread.daemon = True
                self.popup_monitor_thread.start()
                print(f"已启动同步，主控窗口: {self.master_window}, 同步窗口: {self.sync_windows}")
                
            # 添加：将所有窗口设置为置顶
            for hwnd in self.sync_windows:
                try:
                    # 设置窗口为置顶
                    win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, 
                                        win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
                    # 取消置顶（但保持在所有窗口前面）
                    win32gui.SetWindowPos(hwnd, win32con.HWND_NOTOPMOST, 0, 0, 0, 0, 
                                        win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
                except Exception as e:
                    print(f"设置窗口 {hwnd} 置顶失败: {str(e)}")
            
            # 添加：将主窗口设置为活动窗口
            try:
                # 确保主窗口可见
                win32gui.ShowWindow(self.master_window, win32con.SW_RESTORE)
                # 设置主窗口为前台窗口
                win32gui.SetForegroundWindow(self.master_window)
                print(f"已激活主窗口: {self.master_window}")
            except Exception as e:
                print(f"激活主窗口失败: {str(e)}")
                
        except Exception as e:
            self.stop_sync()  # 确保清理资源
            print(f"开启同步失败: {str(e)}")

    def message_loop(self):
        # 消息循环 - 优化版本，降低CPU使用率
        while self.is_syncinging:
            # 增加更长的睡眠时间，减少CPU使用
            time.sleep(0.005)  # 5ms睡眠，平衡响应性和CPU使用率

    def on_mouse_event(self, event):
        try:
            if self.is_syncinging:
                current_window = win32gui.GetForegroundWindow()
                
                # 检查是否是主控窗口或其插件窗口
                is_master = current_window == self.master_window
                master_popups = self.get_chrome_popups(self.master_window)
                
                # 检查是否是主窗口的弹出窗口之一
                is_popup = False
                if not is_master and current_window in master_popups:
                    is_popup = True
                    # 确保这个弹出窗口在我们的同步列表中
                    if current_window not in self.popup_windows:
                        self.popup_windows.append(current_window)
                
                # 只有当当前窗口是主控窗口或其弹出窗口时才处理事件
                # 这样可以防止其他窗口控制同步
                if is_master or is_popup:
                    # 获取鼠标位置
                    x, y = mouse.get_position()
                    
                    # 获取当前窗口的矩形区域
                    current_rect = win32gui.GetWindowRect(current_window)
                    
                    # 检查鼠标是否在当前窗口范围内
                    mouse_in_window = (
                        x >= current_rect[0] and x <= current_rect[2] and
                        y >= current_rect[1] and y <= current_rect[3]
                    )
                    
                    # 只有当鼠标在窗口范围内时才进行同步
                    if not mouse_in_window:
                        return
                    
                    # 对于移动事件进行优化
                    if isinstance(event, mouse.MoveEvent):
                        # 改进的移动事件节流策略
                        current_time = time.time()
                        if not hasattr(self, 'move_interval'):
                            self.move_interval = 0.01  # 10ms节流间隔
                        
                        # 更精细的移动阈值控制
                        if not hasattr(self, 'mouse_threshold'):
                            self.mouse_threshold = 2  # 像素移动阈值
                            
                        # 时间节流：忽略过于频繁的移动事件
                        if current_time - getattr(self, 'last_move_time', 0) < self.move_interval:
                            return
                        
                        # 距离节流：忽略过小的移动
                        last_pos = getattr(self, 'last_mouse_position', (event.x, event.y))
                        dx = abs(event.x - last_pos[0])
                        dy = abs(event.y - last_pos[1])
                        if dx < self.mouse_threshold and dy < self.mouse_threshold:
                            return
                            
                        # 更新上次位置和时间
                        self.last_mouse_position = (event.x, event.y)
                        self.last_move_time = current_time
                    
                    # 计算当前窗口的相对坐标
                    rel_x = (x - current_rect[0]) / max((current_rect[2] - current_rect[0]), 1)
                    rel_y = (y - current_rect[1]) / max((current_rect[3] - current_rect[1]), 1)
                    
                    # 使用线程池批量处理事件分发
                    sync_tasks = []
                    
                    # 同步到其他窗口
                    for hwnd in self.sync_windows:
                        try:
                            # 确定目标窗口
                            if is_master:
                                target_hwnd = hwnd
                            else:
                                # 查找对应的扩展程序窗口
                                target_popups = self.get_chrome_popups(hwnd)

                                # 检查当前窗口是否为弹出类型的浮动窗口
                                style = win32gui.GetWindowLong(current_window, win32con.GWL_STYLE)
                                is_floating = (style & win32con.WS_POPUP) != 0
                                current_title = win32gui.GetWindowText(current_window)
                                
                                if is_floating and target_popups:
                                    # 按照相对位置和窗口标题匹配浮动窗口
                                    best_match = None
                                    min_diff = float('inf')
                                    current_size = (current_rect[2] - current_rect[0], current_rect[3] - current_rect[1])
                                    
                                    for popup in target_popups:
                                        # 获取目标弹出窗口信息
                                        popup_rect = win32gui.GetWindowRect(popup)
                                        popup_style = win32gui.GetWindowLong(popup, win32con.GWL_STYLE)
                                        popup_title = win32gui.GetWindowText(popup)
                                        
                                        # 检查是否也是浮动窗口
                                        if (popup_style & win32con.WS_POPUP) == 0:
                                            continue
                                            
                                        # 计算窗口大小差异
                                        popup_size = (popup_rect[2] - popup_rect[0], popup_rect[3] - popup_rect[1])
                                        size_diff = abs(current_size[0] - popup_size[0]) + abs(current_size[1] - popup_size[1])
                                        
                                        # 计算标题相似度
                                        title_sim = self.title_similarity(current_title, popup_title)
                                        
                                        # 综合评分
                                        diff = size_diff * (2.0 - title_sim)
                                        
                                        if diff < min_diff:
                                            min_diff = diff
                                            best_match = popup
                                    
                                    target_hwnd = best_match if best_match else hwnd
                                else:
                                    # 按照相对位置匹配
                                    best_match = None
                                    min_diff = float('inf')
                                    for popup in target_popups:
                                        popup_rect = win32gui.GetWindowRect(popup)
                                        master_rect = win32gui.GetWindowRect(current_window)
                                        # 计算相对位置差异
                                        master_rel_x = master_rect[0] - win32gui.GetWindowRect(self.master_window)[0]
                                        master_rel_y = master_rect[1] - win32gui.GetWindowRect(self.master_window)[1]
                                        popup_rel_x = popup_rect[0] - win32gui.GetWindowRect(hwnd)[0]
                                        popup_rel_y = popup_rect[1] - win32gui.GetWindowRect(hwnd)[1]
                                        
                                        diff = abs(master_rel_x - popup_rel_x) + abs(master_rel_y - popup_rel_y)
                                        if diff < min_diff:
                                            min_diff = diff
                                            best_match = popup
                                    target_hwnd = best_match if best_match else hwnd
                            
                            if not target_hwnd:
                                continue
                            
                            # 获取目标窗口尺寸
                            target_rect = win32gui.GetWindowRect(target_hwnd)
                            
                            # 计算目标坐标 - 保护除以零
                            client_x = int((target_rect[2] - target_rect[0]) * rel_x)
                            client_y = int((target_rect[3] - target_rect[1]) * rel_y)
                            lparam = win32api.MAKELONG(client_x, client_y)
                            
                            # 使用PostMessage代替SendMessage提高性能
                            # 处理滚轮事件
                            if isinstance(event, mouse.WheelEvent):
                                try:
                                    wheel_delta = int(event.delta)
                                    if keyboard.is_pressed('ctrl'):
                                        if wheel_delta > 0:                                            
                                            win32gui.PostMessage(target_hwnd, win32con.WM_KEYDOWN, win32con.VK_CONTROL, 0)
                                            win32gui.PostMessage(target_hwnd, win32con.WM_KEYDOWN, 0xBB, 0)  # VK_OEM_PLUS
                                            win32gui.PostMessage(target_hwnd, win32con.WM_KEYUP, 0xBB, 0)
                                            win32gui.PostMessage(target_hwnd, win32con.WM_KEYUP, win32con.VK_CONTROL, 0)
                                        else:
                                            win32gui.PostMessage(target_hwnd, win32con.WM_KEYDOWN, win32con.VK_CONTROL, 0)
                                            win32gui.PostMessage(target_hwnd, win32con.WM_KEYDOWN, 0xBD, 0)  # VK_OEM_MINUS
                                            win32gui.PostMessage(target_hwnd, win32con.WM_KEYUP, 0xBD, 0)
                                            win32gui.PostMessage(target_hwnd, win32con.WM_KEYUP, win32con.VK_CONTROL, 0)
                                    else:
                                        # 获取滚轮方向和绝对值
                                        abs_delta = abs(wheel_delta)
                                        scroll_up = wheel_delta > 0
                                        
                                        # 主要使用PageUp/PageDown键来实现更大的滚动幅度
                                        # 对于小幅度滚动，使用箭头键；对于大幅度滚动，使用Page键
                                        
                                        # 根据滚动大小决定策略，微调使同步窗口滚动幅度更接近主窗口
                                        if abs_delta <= 1:
                                            # 对于小幅度滚动，减少到2次箭头键
                                            vk_code = win32con.VK_UP if scroll_up else win32con.VK_DOWN
                                            for _ in range(2):
                                                win32gui.PostMessage(target_hwnd, win32con.WM_KEYDOWN, vk_code, 0)
                                                win32gui.PostMessage(target_hwnd, win32con.WM_KEYUP, vk_code, 0)
                                        elif abs_delta <= 3:
                                            # 对于中等幅度滚动，使用一次Page键但减少额外的箭头键
                                            page_vk = win32con.VK_PRIOR if scroll_up else win32con.VK_NEXT  # Page Up/Down
                                            win32gui.PostMessage(target_hwnd, win32con.WM_KEYDOWN, page_vk, 0)
                                            win32gui.PostMessage(target_hwnd, win32con.WM_KEYUP, page_vk, 0)
                                            
                                            # 额外只增加1次箭头键，减少之前的额外按键
                                            vk_code = win32con.VK_UP if scroll_up else win32con.VK_DOWN
                                            win32gui.PostMessage(target_hwnd, win32con.WM_KEYDOWN, vk_code, 0)
                                            win32gui.PostMessage(target_hwnd, win32con.WM_KEYUP, vk_code, 0)
                                        else:
                                            # 对于大幅度滚动，减少Page键系数
                                            page_count = min(int(abs_delta * 0.4), 2)  # 系数从0.6降到0.4，最多减少到2次
                                            page_vk = win32con.VK_PRIOR if scroll_up else win32con.VK_NEXT
                                            
                                            for _ in range(page_count):
                                                win32gui.PostMessage(target_hwnd, win32con.WM_KEYDOWN, page_vk, 0)
                                                win32gui.PostMessage(target_hwnd, win32con.WM_KEYUP, page_vk, 0)
                                                
                                            # 移除额外的箭头键调整
                                
                                except Exception as e:
                                    print(f"处理滚轮事件失败: {str(e)}")
                                    continue
                            
                            # 处理鼠标点击
                            elif isinstance(event, mouse.ButtonEvent):
                                if event.event_type == mouse.DOWN:
                                    if event.button == mouse.LEFT:
                                        win32gui.PostMessage(target_hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lparam)
                                    elif event.button == mouse.RIGHT:
                                        win32gui.PostMessage(target_hwnd, win32con.WM_RBUTTONDOWN, win32con.MK_RBUTTON, lparam)
                                    elif event.button == mouse.MIDDLE:  # 添加中键支持
                                        win32gui.PostMessage(target_hwnd, win32con.WM_MBUTTONDOWN, win32con.MK_MBUTTON, lparam)
                                elif event.event_type == mouse.UP:
                                    if event.button == mouse.LEFT:
                                        win32gui.PostMessage(target_hwnd, win32con.WM_LBUTTONUP, 0, lparam)
                                    elif event.button == mouse.RIGHT:
                                        win32gui.PostMessage(target_hwnd, win32con.WM_RBUTTONUP, 0, lparam)
                                    elif event.button == mouse.MIDDLE:  # 添加中键支持
                                        win32gui.PostMessage(target_hwnd, win32con.WM_MBUTTONUP, 0, lparam)
                            
                            # 处理鼠标移动 - 减少移动事件传递，仅对实质性移动做处理
                            elif isinstance(event, mouse.MoveEvent):
                                win32gui.PostMessage(target_hwnd, win32con.WM_MOUSEMOVE, 0, lparam)
                                
                        except Exception as e:
                            error_msg = str(e)
                            # 减少错误日志输出频率
                            if not hasattr(self, 'last_error_time') or time.time() - self.last_error_time > 5:
                                print(f"同步到窗口 {hwnd} 失败: {error_msg}")
                                self.last_error_time = time.time()
        except Exception as e:
            print(f"鼠标事件处理总体错误: {str(e)}")

    def on_keyboard_event(self, event):
        # 优化版键盘事件处理
        try:
            if self.is_syncinging:
                current_window = win32gui.GetForegroundWindow()
                
                # 检查是否是主控窗口或其插件窗口
                is_master = current_window == self.master_window
                master_popups = self.get_chrome_popups(self.master_window)
                
                # 检查是否是主窗口的弹出窗口之一
                is_popup = False
                if not is_master and current_window in master_popups:
                    is_popup = True
                    # 确保这个弹出窗口在我们的同步列表中
                    if current_window not in self.popup_windows:
                        self.popup_windows.append(current_window)
                
                # 只有当当前窗口是主控窗口或其弹出窗口时才处理事件
                # 这样可以防止其他窗口控制同步
                if is_master or is_popup:
                    # 获取鼠标位置
                    x, y = mouse.get_position()
                    
                    # 获取当前窗口的矩形区域
                    current_rect = win32gui.GetWindowRect(current_window)
                    
                    # 检查鼠标是否在当前窗口范围内
                    mouse_in_window = (
                        x >= current_rect[0] and x <= current_rect[2] and
                        y >= current_rect[1] and y <= current_rect[3]
                    )
                    
                    # 只有当鼠标在窗口范围内时才进行同步
                    if not mouse_in_window:
                        return
                        
                    # 获取实际的输入目标窗口
                    input_hwnd = win32gui.GetFocus()
                    
                    # 同步到其他窗口 - 键盘事件限流
                    current_time = time.time()
                    if not hasattr(self, 'last_key_time') or current_time - self.last_key_time > 0.01:
                        self.last_key_time = current_time
                    else:
                        # 对于连续的相同按键，适当限流，减少重复输入
                        if hasattr(self, 'last_key') and self.last_key == event.name and event.event_type == keyboard.KEY_DOWN:
                            return
                    
                    # 记录最后一个按键
                    self.last_key = event.name
                    
                    # 同步到其他窗口
                    for hwnd in self.sync_windows:
                        try:
                            # 确定目标窗口
                            if is_master:
                                target_hwnd = hwnd
                            else:
                                # 查找对应的扩展程序窗口
                                target_popups = self.get_chrome_popups(hwnd)
                                # 按照相对位置匹配
                                best_match = None
                                min_diff = float('inf')
                                for popup in target_popups:
                                    popup_rect = win32gui.GetWindowRect(popup)
                                    master_rect = win32gui.GetWindowRect(current_window)
                                    # 计算相对位置差异
                                    master_rel_x = master_rect[0] - win32gui.GetWindowRect(self.master_window)[0]
                                    master_rel_y = master_rect[1] - win32gui.GetWindowRect(self.master_window)[1]
                                    popup_rel_x = popup_rect[0] - win32gui.GetWindowRect(hwnd)[0]
                                    popup_rel_y = popup_rect[1] - win32gui.GetWindowRect(hwnd)[1]
                                    
                                    diff = abs(master_rel_x - popup_rel_x) + abs(master_rel_y - popup_rel_y)
                                    if diff < min_diff:
                                        min_diff = diff
                                        best_match = popup
                                target_hwnd = best_match if best_match else hwnd

                            if not target_hwnd:
                                continue
                                
                            # 检测组合键状态
                            modifiers = 0
                            modifier_keys = {
                                'ctrl': {'pressed': keyboard.is_pressed('ctrl'), 'vk': win32con.VK_CONTROL, 'flag': win32con.MOD_CONTROL},
                                'alt': {'pressed': keyboard.is_pressed('alt'), 'vk': win32con.VK_MENU, 'flag': win32con.MOD_ALT},
                                'shift': {'pressed': keyboard.is_pressed('shift'), 'vk': win32con.VK_SHIFT, 'flag': win32con.MOD_SHIFT}
                            }

                            # 处理修饰键和组合键
                            for mod_name, mod_info in modifier_keys.items():
                                if mod_info['pressed']:
                                    # 按下修饰键
                                    if event.event_type == keyboard.KEY_DOWN:
                                        win32gui.PostMessage(target_hwnd, win32con.WM_KEYDOWN, mod_info['vk'], 0)
                                    
                                    modifiers |= mod_info['flag']

                            # 处理 Ctrl+组合键的特殊情况
                            if modifier_keys['ctrl']['pressed'] and event.name in ['a', 'c', 'v', 'x', 'z']:
                                vk_code = ord(event.name.upper())
                                if event.event_type == keyboard.KEY_DOWN:
                                    # 发送组合键序列
                                    win32gui.PostMessage(target_hwnd, win32con.WM_KEYDOWN, vk_code, 0)
                                    win32gui.PostMessage(target_hwnd, win32con.WM_KEYUP, vk_code, 0)
                                    
                                # 对于这些特殊组合键，直接处理完毕
                                continue
                                
                            # 处理普通按键
                            if event.name in ['enter', 'backspace', 'tab', 'esc', 'space', 
                                            'up', 'down', 'left', 'right', 
                                            'home', 'end', 'page up', 'page down', 'delete', 
                                            'f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9', 'f10', 'f11', 'f12']:  
                                vk_map = {
                                    'enter': win32con.VK_RETURN,
                                    'backspace': win32con.VK_BACK,
                                    'tab': win32con.VK_TAB,
                                    'esc': win32con.VK_ESCAPE,
                                    'space': win32con.VK_SPACE,
                                    'up': win32con.VK_UP,
                                    'down': win32con.VK_DOWN,
                                    'left': win32con.VK_LEFT,      
                                    'right': win32con.VK_RIGHT,    
                                    'home': win32con.VK_HOME,
                                    'end': win32con.VK_END,
                                    'page up': win32con.VK_PRIOR,
                                    'page down': win32con.VK_NEXT,
                                    'delete': win32con.VK_DELETE,
                                    'f1': win32con.VK_F1,
                                    'f2': win32con.VK_F2,
                                    'f3': win32con.VK_F3,
                                    'f4': win32con.VK_F4,
                                    'f5': win32con.VK_F5,
                                    'f6': win32con.VK_F6,
                                    'f7': win32con.VK_F7,
                                    'f8': win32con.VK_F8,
                                    'f9': win32con.VK_F9,
                                    'f10': win32con.VK_F10,
                                    'f11': win32con.VK_F11,
                                    'f12': win32con.VK_F12
                                }
                                vk_code = vk_map[event.name]
                                
                                # 发送按键消息
                                if event.event_type == keyboard.KEY_DOWN:
                                    win32gui.PostMessage(target_hwnd, win32con.WM_KEYDOWN, vk_code, 0)
                                else:
                                    win32gui.PostMessage(target_hwnd, win32con.WM_KEYUP, vk_code, 0)
                            else:
                                # 处理普通字符
                                if len(event.name) == 1:
                                    vk_code = win32api.VkKeyScan(event.name[0]) & 0xFF
                                    if event.event_type == keyboard.KEY_DOWN:
                                        # 直接发送字符消息，更有效
                                        win32gui.PostMessage(target_hwnd, win32con.WM_CHAR, ord(event.name[0]), 0)
                                    continue
                                else:
                                    continue

                            # 释放修饰键 - 仅在按键弹起时释放
                            if event.event_type == keyboard.KEY_UP:
                                for mod_name, mod_info in modifier_keys.items():
                                    if mod_info['pressed']:
                                        win32gui.PostMessage(target_hwnd, win32con.WM_KEYUP, mod_info['vk'], 0)
                                
                        except Exception as e:
                            # 限制错误日志输出频率
                            if not hasattr(self, 'last_key_error_time') or time.time() - self.last_key_error_time > 5:
                                print(f"同步键盘事件到窗口 {hwnd} 失败: {str(e)}")
                                self.last_key_error_time = time.time()
                            
        except Exception as e:
            # 限制错误日志输出频率
            if not hasattr(self, 'last_keyboard_error_time') or time.time() - self.last_keyboard_error_time > 5:
                print(f"处理键盘事件失败: {str(e)}")
                self.last_keyboard_error_time = time.time()

    def stop_sync(self):
        """停止同步 - 优化版，确保资源清理"""
        try:
            # 标记同步状态为False
            self.is_syncinging = False
            
            # 卸载低级滚轮钩子
            self.unhook_wheel()
            
            # 保存当前快捷键设置，用于后续恢复
            current_shortcut = None
            if hasattr(self, 'current_shortcut'):
                current_shortcut = self.current_shortcut
            
            # 保存当前快捷键钩子
            shortcut_hook = None
            if hasattr(self, 'shortcut_hook'):
                shortcut_hook = self.shortcut_hook
                self.shortcut_hook = None  # 临时清除引用，避免被unhook_all移除
            
            # 移除同步相关的键盘钩子，但保留快捷键钩子
            try:
                # 不使用 keyboard.unhook_all()，而是有选择地移除
                # 暂时没有更好的方法来区分钩子，所以先重置然后恢复快捷键
                keyboard.unhook_all()
                print("已移除同步相关的键盘钩子")
            except Exception as e:
                print(f"移除键盘钩子失败: {str(e)}")
            
            # 移除鼠标钩子
            try:
                mouse.unhook_all()
                print("已移除鼠标钩子")
            except Exception as e:
                print(f"移除鼠标钩子失败: {str(e)}")
            
            # 等待线程结束
            if hasattr(self, 'hook_thread') and self.hook_thread:
                try:
                    if self.hook_thread.is_alive():
                        self.hook_thread.join(timeout=0.5)
                except Exception as e:
                    print(f"等待消息循环线程结束失败: {str(e)}")
                self.hook_thread = None
            
            # 等待弹出窗口监控线程结束
            if hasattr(self, 'popup_monitor_thread') and self.popup_monitor_thread:
                try:
                    if self.popup_monitor_thread.is_alive():
                        self.popup_monitor_thread.join(timeout=0.5)
                except Exception as e:
                    print(f"等待弹出窗口监控线程结束失败: {str(e)}")
                self.popup_monitor_thread = None
            
            # 重置关键数据结构
            self.popup_windows = []
            self.sync_popups = {}
            self.sync_windows = []
            
            # 更新按钮状态 - 需要检查按钮是否存在
            if hasattr(self, 'sync_button') and self.sync_button:
                try:
                    self.sync_button.configure(text="▶ 开始同步", style='Accent.TButton')
                except Exception as e:
                    print(f"更新按钮状态失败: {str(e)}")
            
            # 重新设置快捷键 - 确保快捷键在停止同步后仍然有效
            if current_shortcut:
                try:
                    self.set_shortcut(current_shortcut)
                    print(f"已恢复快捷键设置: {current_shortcut}")
                except Exception as e:
                    print(f"恢复快捷键失败: {str(e)}")
                
            # 提示用户
            print("同步已停止")
            
        except Exception as e:
            print(f"停止同步出错: {str(e)}")
            traceback.print_exc()
            # 确保按钮恢复正常状态
            try:
                if hasattr(self, 'sync_button') and self.sync_button:
                    self.sync_button.configure(text="▶ 开始同步", style='Accent.TButton')
            except:
                pass

  
    def enum_window_callback(self, hwnd, windows):
        # 枚举窗口回调函数
        try:
            # 检查窗口是否可见
            if not win32gui.IsWindowVisible(hwnd):
                return
            
            # 获取窗口标题
            title = win32gui.GetWindowText(hwnd)
            if not title:
                return
            
            # 检查是否是Chrome窗口
            if " - Google Chrome" in title:
                # 提取窗口编号
                number = None
                if title.startswith("[主控]"):
                    title = title[4:].strip()  # 移除[主控]标记
                
                # 从进程命令行参数中获取窗口编号
                try:
                    _, pid = win32process.GetWindowThreadProcessId(hwnd)
                    handle = win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION | win32con.PROCESS_VM_READ, False, pid)
                    if handle:
                        cmd_line = win32process.GetModuleFileNameEx(handle, 0)
                        win32api.CloseHandle(handle)
                        
                        # 从路径中提取编号
                        if "\\Data\\" in cmd_line:
                            number = int(cmd_line.split("\\Data\\")[-1].split("\\")[0])
                except:
                    pass
                
                if number is not None:
                    windows.append({
                        'hwnd': hwnd,
                        'title': title,
                        'number': number
                    })
                
        except Exception as e:
            print(f"枚举窗口失败: {str(e)}")

    def get_chrome_popups(self, chrome_hwnd):
        """改进的插件窗口检测，支持网页触发的钱包插件和网页浮动层"""
        popups = []
        def enum_windows_callback(hwnd, _):
            try:
                if not win32gui.IsWindowVisible(hwnd):
                    return
                    
                class_name = win32gui.GetClassName(hwnd)
                title = win32gui.GetWindowText(hwnd)
                _, chrome_pid = win32process.GetWindowThreadProcessId(chrome_hwnd)
                _, popup_pid = win32process.GetWindowThreadProcessId(hwnd)
                
                # 检查是否是Chrome相关窗口
                if popup_pid == chrome_pid:
                    # 检查窗口类型
                    if "Chrome_WidgetWin" in class_name:  # 放宽类名匹配条件
                        # 检查是否是扩展程序相关窗口，放宽检测条件
                        style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
                        ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
                        
                        # 扩展窗口的特征
                        is_popup = (
                            "扩展程序" in title or 
                            "插件" in title or
                            "OKX" in title or  # 常见钱包名称
                            "MetaMask" in title or  # 常见钱包名称
                            "钱包" in title or
                            "Wallet" in title or
                            win32gui.GetParent(hwnd) == chrome_hwnd or
                            (style & win32con.WS_POPUP) != 0 or
                            (style & win32con.WS_CHILD) != 0 or
                            (ex_style & win32con.WS_EX_TOOLWINDOW) != 0 or
                            (ex_style & win32con.WS_EX_DLGMODALFRAME) != 0  # 对话框样式窗口
                        )
                        
                        # 获取窗口位置和大小，钱包插件通常较小
                        rect = win32gui.GetWindowRect(hwnd)
                        width = rect[2] - rect[0]
                        height = rect[3] - rect[1]
                        
                        # 钱包插件窗口通常不会特别大
                        is_wallet_size = (width < 800 and height < 800 and width > 200 and height > 200)
                        
                        # 网页浮动层通常是较小的弹窗
                        is_floating_layer = (
                            (style & win32con.WS_POPUP) != 0 and
                            (width < 600 and height < 600) and
                            hwnd != chrome_hwnd
                        )
                        
                        if is_popup or is_wallet_size or is_floating_layer:
                            # 增加额外判断，如果窗口很像钱包弹窗，即使不满足其他条件也捕获
                            if hwnd != chrome_hwnd and hwnd not in popups:
                                if self.is_likely_wallet_popup(hwnd, chrome_hwnd) or is_floating_layer:
                                    popups.append(hwnd)
                                    print(f"识别到可能的钱包插件窗口或网页浮动层: {title} (句柄: {hwnd})")
                                elif is_popup:
                                    popups.append(hwnd)
                    
            except Exception as e:
                print(f"枚举窗口失败: {str(e)}")
                
        win32gui.EnumWindows(enum_windows_callback, None)
        return popups
        
    def monitor_popups(self):
        """监控Chrome弹出窗口，改进以更好地支持钱包插件窗口"""
        last_check_time = time.time()
        last_error_time = 0
        error_count = 0
        
        # 钱包插件窗口同步历史
        wallet_popup_history = {}
        
        print("启动弹窗监控线程...")
        
        while self.is_syncinging:
            try:
                # 优化CPU使用率
                time.sleep(0.1)  # 更快速的检查以捕获快速弹出的钱包窗口
                
                # 每500毫秒执行一次完整检查
                current_time = time.time()
                if current_time - last_check_time < 0.5:
                    continue
                    
                last_check_time = current_time
                
                # 检查主窗口是否有效
                if not self.master_window or not win32gui.IsWindow(self.master_window):
                    if current_time - last_error_time > 10:
                        print("主窗口无效，停止同步")
                        last_error_time = current_time
                    self.stop_sync()
                    break
                
                # 获取主窗口的弹出窗口
                current_popups = self.get_chrome_popups(self.master_window)
                
                # 检查是否有新增弹出窗口或关闭的弹出窗口
                new_popups = [popup for popup in current_popups if popup not in self.popup_windows]
                closed_popups = [popup for popup in self.popup_windows if popup not in current_popups]
                
                has_changes = False
                
                # 处理新的弹出窗口，特别注意钱包插件窗口
                for popup in new_popups:
                    try:
                        if self.is_syncing and win32gui.IsWindow(popup):
                            # 获取窗口标题
                            title = win32gui.GetWindowText(popup)
                            
                            # 检查是否是钱包插件窗口
                            is_wallet = self.is_likely_wallet_popup(popup, self.master_window)
                            
                            if is_wallet:
                                print(f"发现钱包插件窗口: {title}")
                                # 记录钱包窗口信息用于后续处理
                                wallet_popup_history[popup] = {
                                    'detected_time': time.time(),
                                    'title': title,
                                    'synced': False
                                }
                            
                            # 将弹出窗口添加到同步列表
                            if popup not in self.popup_windows:
                                self.popup_windows.append(popup)
                                has_changes = True
                    except Exception as e:
                        if current_time - last_error_time > 10:
                            print(f"处理新弹窗时出错: {str(e)}")
                            last_error_time = current_time
                
                # 清理已关闭的弹出窗口
                for popup in closed_popups:
                    if popup in self.popup_windows:
                        self.popup_windows.remove(popup)
                        if popup in wallet_popup_history:
                            del wallet_popup_history[popup]
                        has_changes = True
                
                # 同步处理钱包窗口和其他弹出窗口
                if has_changes:
                    self.sync_popups()
                    
                # 定期尝试同步钱包插件窗口，即使没有检测到变化
                # 这有助于处理某些难以检测的网页触发钱包窗口
                for hwnd, info in list(wallet_popup_history.items()):
                    if (not info.get('synced') and 
                        current_time - info.get('detected_time', 0) > 0.5 and
                        win32gui.IsWindow(hwnd)):
                        # 尝试强制同步钱包窗口
                        try:
                            self.sync_specific_popup(hwnd)
                            info['synced'] = True
                            print(f"强制同步钱包窗口: {info['title']}")
                        except Exception as e:
                            if current_time - last_error_time > 10:
                                print(f"强制同步钱包窗口失败: {str(e)}")
                                last_error_time = current_time
                
                # 清理无效的历史记录
                for hwnd in list(wallet_popup_history.keys()):
                    if not win32gui.IsWindow(hwnd) or current_time - wallet_popup_history[hwnd]['detected_time'] > 60:
                        del wallet_popup_history[hwnd]
                
            except Exception as e:
                error_count += 1
                
                # 限制错误日志频率
                if current_time - last_error_time > 10:
                    print(f"弹出窗口监控异常: {str(e)}")
                    last_error_time = current_time
                    
                # 防止过多错误导致CPU占用过高
                if error_count > 100:
                    print("错误次数过多，停止弹窗监控")
                    break
                    
                time.sleep(1)  # 出错后等待一段时间
                
        print("弹窗监控线程已结束")
        
       
 
    def sync_popups(self):
        """同步主窗口的弹出窗口到所有同步窗口，改进对网页浮动层的处理"""
        try:
            if not self.is_syncing or not self.master_window or not win32gui.IsWindow(self.master_window):
                return
                
            # 获取主窗口的所有弹出窗口
            master_popups = self.get_chrome_popups(self.master_window)
            if not master_popups:
                return
                
            # 获取主窗口位置
            master_rect = win32gui.GetWindowRect(self.master_window)
            master_x = master_rect[0]
            master_y = master_rect[1]
            
            # 针对每个主窗口的弹出窗口进行同步
            for popup in master_popups:
                try:
                    if not win32gui.IsWindow(popup):
                        continue
                        
                    # 获取弹出窗口位置和大小
                    popup_rect = win32gui.GetWindowRect(popup)
                    popup_width = popup_rect[2] - popup_rect[0]
                    popup_height = popup_rect[3] - popup_rect[1]
                    
                    # 检查窗口样式，确定是否为网页浮动层
                    style = win32gui.GetWindowLong(popup, win32con.GWL_STYLE)
                    ex_style = win32gui.GetWindowLong(popup, win32con.GWL_EXSTYLE)
                    
                    is_floating_layer = (
                        (style & win32con.WS_POPUP) != 0 and
                        (popup_width < 600 and popup_height < 600)
                    )
                    
                    # 计算相对于主窗口的位置
                    rel_x = popup_rect[0] - master_x
                    rel_y = popup_rect[1] - master_y
                    
                    # 同步到所有其他窗口
                    for hwnd in self.sync_windows:
                        if hwnd != self.master_window and win32gui.IsWindow(hwnd):
                            # 获取同步窗口位置
                            sync_rect = win32gui.GetWindowRect(hwnd)
                            sync_x = sync_rect[0]
                            sync_y = sync_rect[1]
                            
                            # 获取该窗口的所有弹出窗口
                            sync_popups = self.get_chrome_popups(hwnd)
                            
                            # 寻找可能匹配的弹出窗口
                            target_title = win32gui.GetWindowText(popup)
                            best_match = None
                            best_score = 0
                            
                            # 对网页浮动层和其他弹出窗口应用不同的匹配策略
                            if is_floating_layer:
                                # 为浮动层寻找相似的大小和位置
                                for sync_popup in sync_popups:
                                    if not win32gui.IsWindow(sync_popup):
                                        continue
                                        
                                    sync_style = win32gui.GetWindowLong(sync_popup, win32con.GWL_STYLE)
                                    
                                    # 检查是否同样是弹出样式
                                    if (sync_style & win32con.WS_POPUP) == 0:
                                        continue
                                        
                                    # 对于网页浮动层，主要基于尺寸和位置相似度匹配
                                    sync_rect = win32gui.GetWindowRect(sync_popup)
                                    sync_width = sync_rect[2] - sync_rect[0]
                                    sync_height = sync_rect[3] - sync_rect[1]
                                    
                                    # 尺寸相似度
                                    size_match = 1.0 - min(1.0, (abs(sync_width - popup_width) / max(popup_width, 1) + 
                                                       abs(sync_height - popup_height) / max(popup_height, 1)) / 2)
                                    
                                    # 相对位置相似度
                                    sync_rel_x = sync_rect[0] - sync_x
                                    sync_rel_y = sync_rect[1] - sync_y
                                    pos_match = 1.0 - min(1.0, (abs(sync_rel_x - rel_x) + abs(sync_rel_y - rel_y)) / 
                                                   max(sync_rect[2] - sync_rect[0] + sync_rect[3] - sync_rect[1], 1))
                                    
                                    # 综合得分，对于浮动层位置更重要
                                    score = size_match * 0.4 + pos_match * 0.6
                                    
                                    if score > best_score and score > 0.6:  # 提高匹配阈值
                                        best_score = score
                                        best_match = sync_popup
                            else:
                                # 对于普通弹出窗口，使用标题和尺寸综合匹配
                                for sync_popup in sync_popups:
                                    if not win32gui.IsWindow(sync_popup):
                                        continue
                                        
                                    sync_title = win32gui.GetWindowText(sync_popup)
                                    # 计算标题相似度
                                    similarity = self.title_similarity(target_title, sync_title)
                                    
                                    # 获取窗口大小相似度
                                    sync_rect = win32gui.GetWindowRect(sync_popup)
                                    sync_width = sync_rect[2] - sync_rect[0]
                                    sync_height = sync_rect[3] - sync_rect[1]
                                    size_match = min(1.0, 1.0 - (abs(sync_width - popup_width) + abs(sync_height - popup_height)) / 
                                                     max(popup_width + popup_height, 1))
                                    
                                    # 计算总匹配分数
                                    score = similarity * 0.7 + size_match * 0.3
                                    if score > best_score and score > 0.5:
                                        best_score = score
                                        best_match = sync_popup
                            
                            # 如果找到匹配的弹出窗口，调整其位置
                            if best_match:
                                # 计算新位置
                                new_x = sync_x + rel_x
                                new_y = sync_y + rel_y
                                
                                # 设置窗口位置
                                win32gui.SetWindowPos(
                                    best_match,
                                    win32con.HWND_TOP,
                                    new_x, new_y,
                                    popup_width, popup_height,
                                    win32con.SWP_NOACTIVATE
                                )
                            elif is_floating_layer:
                                # 如果是浮动层但没找到匹配项，尝试通过模拟点击关闭和重新打开的方式同步
                                print(f"找不到匹配的浮动层，尝试通过其他方式同步")
                                # 这里可以实现其他同步策略，如向目标窗口发送模拟点击
                                # 由于模拟点击可能较复杂，这里只记录日志
                except Exception as e:
                    print(f"同步单个弹窗出错: {str(e)}")
                    
        except Exception as e:
            print(f"同步弹窗过程出错: {str(e)}")

    def setup_wheel_hook(self):
        """设置全局滚轮钩子"""
        if self.wheel_hook_id:
            # 如果已经有钩子，先卸载
            self.unhook_wheel()
        
        # 定义钩子回调函数
        def wheel_proc(nCode, wParam, lParam):
            try:
                # 检查是否为滚轮消息
                if wParam == win32con.WM_MOUSEWHEEL and self.is_syncing:
                    # 获取当前窗口
                    current_window = win32gui.GetForegroundWindow()
                    
                    # 检查是否为主控窗口
                    is_master_window = current_window == self.master_window
                    
                    # 获取主窗口的弹出窗口
                    master_popups = self.get_chrome_popups(self.master_window)
                    
                    # 判断是否为主窗口的插件
                    is_master_plugin = current_window in master_popups
                    
                    # 如果不是主控窗口也不是主窗口插件，直接放行事件
                    if not is_master_window and not is_master_plugin:
                        return ctypes.windll.user32.CallNextHookEx(self.wheel_hook_id, nCode, wParam, ctypes.cast(lParam, ctypes.c_void_p))
                    
                    # 获取窗口层次结构信息
                    try:
                        # 获取窗口类名和标题
                        window_class = win32gui.GetClassName(current_window)
                        window_title = win32gui.GetWindowText(current_window)
                        
                        # 获取窗口样式
                        style = win32gui.GetWindowLong(current_window, win32con.GWL_STYLE)
                        ex_style = win32gui.GetWindowLong(current_window, win32con.GWL_EXSTYLE)
                        
                        # 获取窗口进程ID
                        _, process_id = win32process.GetWindowThreadProcessId(current_window)
                        _, master_process_id = win32process.GetWindowThreadProcessId(self.master_window)
                        
                        # 获取位置和尺寸
                        rect = win32gui.GetWindowRect(current_window)
                        width = rect[2] - rect[0]
                        height = rect[3] - rect[1]
                    except:
                        window_class = ""
                        window_title = ""
                        style = 0
                        ex_style = 0
                        process_id = 0
                        master_process_id = 0
                        width = 0
                        height = 0
                    
                    # 检查是否为无法用键盘控制滚动的特殊窗口
                    is_uncontrollable_window = False
                    if "Chrome_RenderWidgetHostHWND" in window_class:
                        is_uncontrollable_window = True
                    
                    # 检查是否与Chrome相关
                    is_chrome_window = (
                        "Chrome_" in window_class or 
                        "Chromium_" in window_class
                    )
                    
                    # 检查是否是插件窗口
                    is_plugin_window = is_master_plugin
                    
                    if is_master_plugin:
                        print(f"识别到主窗口插件: {window_title}, 句柄: {current_window}")
                    
                    # 检查Ctrl键状态 - 如果按下Ctrl则不拦截事件（保留缩放功能）
                    ctrl_pressed = ctypes.windll.user32.GetKeyState(win32con.VK_CONTROL) & 0x8000 != 0
                    if ctrl_pressed and is_chrome_window:
                        print("检测到Ctrl键按下，不拦截滚轮事件(保留缩放功能)")
                        # 不拦截，让事件继续传递给Chrome处理缩放
                        return ctypes.windll.user32.CallNextHookEx(self.wheel_hook_id, nCode, wParam, ctypes.cast(lParam, ctypes.c_void_p))
                    
                    # 只处理Chrome相关窗口且不是无法控制的特殊窗口
                    if is_chrome_window and not is_uncontrollable_window:
                        # 防止过于频繁触发
                        current_time = time.time()
                        if current_time - self.last_wheel_time < self.wheel_threshold:
                            # 阻止事件继续传递（返回1）
                            return 1
                        
                        self.last_wheel_time = current_time
                        
                        # 从MSLLHOOKSTRUCT结构体中获取滚轮增量
                        wheel_delta = ctypes.c_short(lParam.contents.mouseData >> 16).value
                        
                        # 标准化滚轮增量
                        normalized_delta = self.normalize_wheel_delta(wheel_delta)
                        
                        # 只同步到其他同步窗口，不包括主窗口自身
                        windows_to_sync = self.sync_windows
                        
                        # 获取鼠标位置
                        mouse_x, mouse_y = lParam.contents.pt.x, lParam.contents.pt.y
                        print(f"拦截滚轮事件: 窗口={current_window}, 类型={'主窗口' if is_master_window else '主窗口插件' if is_master_plugin else '其他'}, wheel_delta={wheel_delta}")
                        
                        # 如果是插件窗口，同步到其他窗口，但允许原始事件继续传递
                        if is_plugin_window:
                            # 向同步窗口发送模拟滚动
                            if windows_to_sync:
                                print(f"主窗口插件滚轮事件，同步到其他{len(windows_to_sync)}个窗口")
                                self.sync_specified_windows_scroll(normalized_delta, windows_to_sync)
                            
                            # 允许原始事件继续传递，这样插件窗口本身可以正常滚动
                            print("允许插件窗口原始滚轮事件继续传递")
                            return ctypes.windll.user32.CallNextHookEx(self.wheel_hook_id, nCode, wParam, ctypes.cast(lParam, ctypes.c_void_p))
                        
                        # 主窗口：拦截原始事件，向同步窗口发送模拟滚动
                        else:
                            # 包括主窗口在内的所有窗口
                            all_windows = [self.master_window] + self.sync_windows
                            print(f"主窗口滚轮事件，同步到所有{len(all_windows)}个窗口")
                            self.sync_specified_windows_scroll(normalized_delta, all_windows)
                            # 拦截原始滚轮事件
                            return 1
                
                # 其他消息或非Chrome窗口，继续传递事件
                return ctypes.windll.user32.CallNextHookEx(self.wheel_hook_id, nCode, wParam, ctypes.cast(lParam, ctypes.c_void_p))
                
            except Exception as e:
                print(f"滚轮钩子处理出错: {str(e)}")
                # 异常情况下继续传递事件
                return ctypes.windll.user32.CallNextHookEx(self.wheel_hook_id, nCode, wParam, ctypes.cast(lParam, ctypes.c_void_p))
            
        # 创建钩子回调函数
        self.wheel_hook_proc = ctypes.WINFUNCTYPE(
            ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.POINTER(MSLLHOOKSTRUCT)
        )(wheel_proc)
        
        try:
            # 安装钩子 - 修复整数溢出错误，直接使用0而不是GetModuleHandle(None)
            self.wheel_hook_id = ctypes.windll.user32.SetWindowsHookExW(
                win32con.WH_MOUSE_LL,
                self.wheel_hook_proc,
                0,  # 直接使用0替代win32api.GetModuleHandle(None)
                0
            )
            
            if not self.wheel_hook_id:
                error = ctypes.windll.kernel32.GetLastError()
                raise Exception(f"安装滚轮钩子失败，错误码: {error}")
                
        except Exception as e:
            print(f"安装滚轮钩子时出错: {str(e)}")
            # 确保标记为None，以便其他部分代码知道钩子未成功安装
            self.wheel_hook_id = None
            raise

    def unhook_wheel(self):
        """卸载滚轮钩子"""
        if self.wheel_hook_id:
            try:
                if ctypes.windll.user32.UnhookWindowsHookEx(self.wheel_hook_id):
                    print("已卸载滚轮钩子")
                else:
                    error = ctypes.windll.kernel32.GetLastError()
                    print(f"卸载滚轮钩子失败，错误码: {error}")
            except Exception as e:
                print(f"卸载滚轮钩子时出错: {str(e)}")
            finally:
                self.wheel_hook_id = None
                self.wheel_hook_proc = None
    
    def normalize_wheel_delta(self, delta, is_plugin=False):
        """标准化滚轮增量值 - 使用适中的缩放系数"""
        # 检查是否可能来自触控板（通常有小数或不规则值）
        abs_delta = abs(delta)

        # 使用适中的缩放系数，不区分窗口类型
        if abs_delta < 40:  # 很小的值，可能是精确触控板
            normalized = delta * 0.20  # 适中系数
        elif abs_delta < 80:  # 中等值
            normalized = delta * 0.25  # 适中系数
        else:  # 标准鼠标滚轮
            normalized = delta * 0.30  # 适中系数

        # 保持方向一致，但标准化大小
        direction = 1 if delta > 0 else -1
        # 标准增量设为中等值，从120降至50
        reduced_wheel_delta = int(self.standard_wheel_delta * 0.42)
        return direction * reduced_wheel_delta

    def load_settings(self):
        """加载设置 - 简化版"""
        return {}

    def title_similarity(self, title1: str, title2: str) -> float:
        """计算标题相似度"""
        if not title1 or not title2:
            return 0.0

        # 简单的字符串匹配
        if title1 == title2:
            return 1.0

        # 检查包含关系
        if title1 in title2 or title2 in title1:
            return 0.8

        # 检查共同词汇
        words1 = set(title1.lower().split())
        words2 = set(title2.lower().split())
        common = words1.intersection(words2)

        if common:
            return len(common) / max(len(words1), len(words2))

        return 0.0

    def is_likely_wallet_popup(self, hwnd: int, parent_hwnd: int) -> bool:
        """检查是否是钱包弹出窗口"""
        try:
            title = win32gui.GetWindowText(hwnd).lower()

            # 钱包相关关键词
            wallet_keywords = [
                'metamask', 'okx', 'wallet', '钱包', 'coinbase',
                'trust', 'phantom', 'connect', 'approve', 'confirm',
                '连接', '授权', '确认', '签名'
            ]

            for keyword in wallet_keywords:
                if keyword in title:
                    return True

            # 检查窗口大小 - 钱包弹窗通常较小
            rect = win32gui.GetWindowRect(hwnd)
            width = rect[2] - rect[0]
            height = rect[3] - rect[1]

            # 典型钱包弹窗尺寸
            if 200 < width < 500 and 300 < height < 700:
                return True

            return False
        except:
            return False

    def sync_specified_windows_scroll(self, delta: int, windows: list):
        """向指定窗口发送滚动事件"""
        try:
            for hwnd in windows:
                if win32gui.IsWindow(hwnd):
                    # 发送滚轮事件
                    wparam = delta << 16
                    win32gui.PostMessage(hwnd, win32con.WM_MOUSEWHEEL, wparam, 0)
        except Exception as e:
            print(f"发送滚动事件失败: {e}")

    def sync_specific_popup(self, popup_hwnd: int):
        """同步特定弹出窗口"""
        try:
            if not win32gui.IsWindow(popup_hwnd):
                return

            popup_rect = win32gui.GetWindowRect(popup_hwnd)

            # 简单的位置同步 - 这里可以根据需要扩展
            print(f"同步弹出窗口: {popup_hwnd}")

        except Exception as e:
            print(f"同步弹出窗口失败: {e}")

 
