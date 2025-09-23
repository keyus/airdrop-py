
from DrissionPage import Chromium
from typing import Dict, Any
import psutil
import ctypes
import win32gui
import win32process
from .app import chrome_process
from .chrome_sync import ChromeManager

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
min_height = screen_width/scale
min_width = 500


class ChromeInstanceController:
    """单个Chrome实例控制器"""

    def __init__(self, name: str, port: int, pid= int, window_index: int = 0):
        self.name = name
        self.port = port
        self.pid = pid
        self.window_index = window_index  # 窗口索引，用于计算位置
        self.browser = None
        self.tab = None
        self.is_active = False
        self.last_url = None
        self.sync_callback = None  # 同步回调函数
        self.hwnd = None  # 窗口句柄

    def connect(self) -> bool:
        """连接到现有Chrome实例"""
        try:
            # 连接到已运行的Chrome实例
            self.browser = Chromium(self.port)
            self.tab = self.browser.latest_tab
            # 设置窗口大小
            self.tab.set.window.size(min_width, min_height)
            # 获取设置后的真实尺寸
            current_width,_ = self.tab.rect.size
            x_position = self.window_index * (current_width/scale)
            print(f"窗口 {self.window_index} 的x位置: {x_position}")
            # 设置窗口位置
            self.tab.set.window.location(x_position, 0)
            self.is_active = True
            print(f"成功连接到实例 {self.name} (端口:{self.port})")
            return True
        except Exception as e:
            print(f"连接实例 {self.name} 失败: {e}")
            return False
    def disconnect(self):
        try:
            if self.browser:
                self.browser.latest_tab.disconnect()
            self.is_active = False
            print(f"已断开实例 {self.name} 的连接")
        except Exception as e:
            print(f"断开实例 {self.name} 连接失败: {e}")

    def get_window_handle(self, pid):
        """为指定进程查找窗口句柄"""
        def enum_callback(hwnd, process_windows):
            if win32gui.IsWindowVisible(hwnd):
                try:
                    _, win_pid = win32process.GetWindowThreadProcessId(hwnd)
                    if win_pid == pid:
                        title = win32gui.GetWindowText(hwnd)
                        class_name = win32gui.GetClassName(hwnd)

                        # 确保是Chrome主窗口
                        if (class_name == "Chrome_WidgetWin_1" and
                            title and
                            not title.startswith("Chrome 传递")):
                            process_windows.append(hwnd)
                except:
                    pass
            return True

        process_windows = []
        win32gui.EnumWindows(enum_callback, process_windows)
        return process_windows[0] if process_windows else None


class Sync:
    """主控同步器"""

    def __init__(self):
        self.master_instance = None  # 主控实例
        self.slave_instances = {}    # 被控实例
        self.chrome = ChromeManager()
        
    # 窗口排列
    def start(self) -> Dict[str, Any]:
        try:
            if not chrome_process:
                return {"success": False, "error": "没有运行中的Chrome实例，请先启动Chrome"}
            # 以第一个Chrome进程作为主控实例
            master_process = chrome_process[0]
            master_name = master_process["name"]
            master_port = master_process.get('debugging_port')
            print(f"选择主控实例: {master_name} (端口: {master_port})")

            # 创建主控实例控制器
            self.master_instance = ChromeInstanceController(
                name=master_name,
                port=master_port,
                pid=master_process.get('pid'),
                window_index=0  # 主控实例在最左边
            )
            if not self.master_instance.connect():
                return {"success": False, "error": f"连接主控实例失败: {master_name}"}

            # 设置主控实例
            hwnd = self.master_instance.get_window_handle(self.master_instance.pid)
            self.chrome.set_master_window(hwnd)
            
            
            # 受控实例连接
            for index, process in enumerate(chrome_process[1:], start=1):  # 从第二个开始，索引从1开始
                slave_name = process["name"]
                slave_port = process.get('debugging_port')
                slave_pid = process.get('pid')
                print(f"正在连接被控实例: {slave_name} (端口:{slave_port})")
                slave_controller = ChromeInstanceController(
                    name=slave_name,
                    port=slave_port,
                    pid=slave_pid,
                    window_index=index  
                )
                if slave_controller.connect():
                    self.slave_instances[slave_name] = slave_controller
                    slave_controller.disconnect()
                    
                hwnd = slave_controller.get_window_handle(slave_pid)
                self.chrome.add_sync_window(hwnd, index)
                    
            # 开始同步
            self.chrome.start_sync()
            return {
                "success": True,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


    