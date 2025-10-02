import threading
import win32gui
import time
import keyboard
import mouse
from .app import chrome_process
from .window.util import Util


class Sync:
    def __init__(self):
        self.util = Util()
        self.master_window = None  # 主控实例
        self.sync_windows = []      # 受控
        self.hook_thread = None  # hooks监听线程
        self.is_running = False  # 运行状态标志
        self.is_sync = False
        self.keyboard_hook = None  # 保存键盘钩子引用
        self.mouse_hook = None  # 保存鼠标钩子引用

    #排列
    def sort_chrome(self):
        for i, it in enumerate(chrome_process):
            self.util.set_position(it.get('hwnd'), i)
            
    #获取同步状态
    def get_sync_status(self):
        return {
            "success": True, 
            "data": self.is_sync,
        }

    def start(self):
        if len(chrome_process) < 2:
            return {
                "success": False,
                "message": "没有同步窗口"
            }
        if self.is_sync:
            return {
                "success": True,
                "message": "已开启同步操作"
            }
        self.sort_chrome()
        self.master_window = chrome_process[0].get('hwnd')
        self.sync_windows = [it.get('hwnd') for it in chrome_process[1:]]
        print('同步窗口：', self.sync_windows)
        self.is_sync = True
        self.sync()
        return {
            "success": True,
            "message": "已开启同步操作"
        }
    def stop(self):
        if not self.is_sync:
            return
        self.is_sync = False
        self.util.reset_const()
        # 只移除当前同步功能的钩子，不影响其他钩子
        if self.keyboard_hook is not None:
            keyboard.unhook(self.keyboard_hook)
            self.keyboard_hook = None
        if self.mouse_hook is not None:
            mouse.unhook(self.mouse_hook)
            self.mouse_hook = None
        if hasattr(self, 'hook_thread') and self.hook_thread and self.hook_thread.is_alive():
            self.hook_thread.join(timeout=0.5)
        print('已取消同步')
    
    def sync(self):
        if not hasattr(self, 'hook_thread') or not self.hook_thread or not self.hook_thread.is_alive():
            self.hook_thread = threading.Thread(target=self.message_loop)
            self.hook_thread.daemon = True
            self.hook_thread.start()
            # 保存钩子引用以便后续精确移除
            self.keyboard_hook = keyboard.hook(self.on_keyboard_event)
            self.mouse_hook = mouse.hook(self.on_mouse_event)
            print("已设置键盘和鼠标钩子")
    def message_loop(self):
        # 消息循环 - 优化版本，降低CPU使用率
        while self.is_sync:
            time.sleep(10)  # 5ms睡眠，平衡响应性和CPU使用率
    #事件检查
    def event_check(self):
        if not self.is_sync:
            return False
        #检查当前窗口是否为主控窗口
        current_window_hwnd = win32gui.GetForegroundWindow()
        is_master = current_window_hwnd == self.master_window
        #是否是chrome类型的窗口,包含插件
        if not self.util.is_chrome_window(current_window_hwnd):
        # if not is_master:
            return False
        #检查鼠标事件是否在当前窗口
        mouse_pos = mouse.get_position()
        current_rect = win32gui.GetWindowRect(current_window_hwnd)
        if not self.util.is_pos_in_window(mouse_pos, current_rect):
            return False
        return (mouse_pos,current_rect,is_master)
        
    #鼠标事件
    def on_mouse_event(self, event):
        check = self.event_check()
        if check is False:
            return 
        mouse_pos,current_rect,is_master = check
        try:
            # 移动节流
            if isinstance(event, mouse.MoveEvent) and not self.util.mouse_throttling(event):
                return 
            # 计算当前窗口的相对坐标
            current_window_mouse_pos = self.util.get_pos_in_window(mouse_pos, current_rect)
            # 事件位于主控窗口
            if is_master:
                # 主空窗口同步到其他窗口
                for hwnd in self.sync_windows:
                    self.util.sync_hwnd(event,hwnd, current_window_mouse_pos)
            # 事件位于弹窗,会枚举当前chrome类型的弹窗
            else:
                pop_hwnd = self.util.get_pop(self.sync_windows)
                # print('弹窗句柄:',pop_hwnd,)
                for hwnd in pop_hwnd:
                    self.util.sync_hwnd(event,hwnd, current_window_mouse_pos)

        except Exception as e:
            pass
        
    def on_keyboard_event(self, event):
        # 优化版键盘事件处理
        check = self.event_check()
        if not check or not self.util.keyboard_throttling(event):
            return 
        # 同步到其他窗口
        for hwnd in self.sync_windows:
            self.util.keyboard_press(event,hwnd)
