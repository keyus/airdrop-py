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
# 检查是否具有管理员权限
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

class ChromeManager:
    def __init__(self):
        self.sync_windows = {}
        self.master_window = None
        self.is_syncinging = False

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
                except Exception as e:
                    print(f"设置钩子失败: {str(e)}")
                    self.stop_sync()
                    raise Exception(f"无法设置输入钩子: {str(e)}")
                
                
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
                
                # 这样可以防止其他窗口控制同步
                if is_master:
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
                
                # 这样可以防止其他窗口控制同步
                if is_master :
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
        try:
            self.is_syncinging = False
            try:
                keyboard.unhook_all()
            except Exception as e:
                print(f"移除键盘钩子失败: {str(e)}")
            
            try:
                mouse.unhook_all()
            except Exception as e:
                print(f"移除鼠标钩子失败: {str(e)}")
            
            self.sync_popups = {}
            self.sync_windows = []
        except Exception as e:
            print('停止同步出现错误',e)
           
  
   
   
 
