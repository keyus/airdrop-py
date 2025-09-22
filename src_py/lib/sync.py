
from DrissionPage import Chromium
from typing import Dict, Any
import ctypes
import threading
import time
from .app import chrome_process

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

    def __init__(self, name: str, port: int, window_index: int = 0):
        self.name = name
        self.port = port
        self.window_index = window_index  # 窗口索引，用于计算位置
        self.browser = None
        self.tab = None
        self.is_active = False
        self.last_url = None
        self.sync_callback = None  # 同步回调函数

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
        """断开连接（不关闭Chrome进程）"""
        try:
            if self.browser:
                self.browser.latest_tab.disconnect()
            self.is_active = False
            print(f"已断开实例 {self.name} 的连接")
        except Exception as e:
            print(f"断开实例 {self.name} 连接失败: {e}")

    def execute_action(self, action: str, **kwargs) -> Dict[str, Any]:
        """执行操作"""
        if not self.is_active or not self.tab:
            return {"success": False, "error": "实例未激活"}

        try:
            if action == "navigate":
                url = kwargs.get("url")
                # 直接导航，使用DrissionPage原生方法
                self.tab.get(url)
                return {"success": True, "message": f"导航到 {url}"}

            elif action == "click":
                selector = kwargs.get("selector")
                element = self.tab.ele(selector)
                if element:
                    element.click()
                    return {"success": True, "message": f"点击 {selector}"}
                else:
                    return {"success": False, "error": f"未找到元素 {selector}"}

            elif action == "input":
                selector = kwargs.get("selector")
                text = kwargs.get("text")
                element = self.tab.ele(selector)
                if element:
                    element.input(text, clear=True)
                    return {"success": True, "message": f"输入文本到 {selector}"}
                else:
                    return {"success": False, "error": f"未找到元素 {selector}"}

            elif action == "scroll":
                x = kwargs.get("x", 0)
                y = kwargs.get("y", 500)
                # 如果有具体的y值，则滚动到指定位置
                if "y" in kwargs:
                    script = f"window.scrollTo({x}, {y});"
                    self.tab.run_js(script)
                else:
                    # 否则使用默认滚动行为
                    self.tab.scroll.to_bottom() if y > 0 else self.tab.scroll.to_top()
                return {"success": True, "message": f"滚动页面到 ({x}, {y})"}

            elif action == "get_title":
                title = self.tab.title
                return {"success": True, "title": title}

            elif action == "get_url":
                url = self.tab.url
                return {"success": True, "url": url}

            elif action == "screenshot":
                # DrissionPage截图功能
                screenshot_path = f"./screenshots/{self.name}_{int(time.time())}.png"
                self.tab.get_screenshot(path=screenshot_path)
                return {"success": True, "screenshot_path": screenshot_path}

            elif action == "execute_script":
                script = kwargs.get("script")
                result = self.tab.run_js(script)
                return {"success": True, "result": result}

            elif action == "wait_element":
                selector = kwargs.get("selector")
                timeout = kwargs.get("timeout", 10)
                element = self.tab.wait.ele_loaded(selector, timeout=timeout)
                if element:
                    return {"success": True, "message": f"元素 {selector} 已加载"}
                else:
                    return {"success": False, "error": f"等待元素 {selector} 超时"}

            else:
                return {"success": False, "error": f"未知操作: {action}"}

        except Exception as e:
            return {"success": False, "error": f"执行操作失败: {str(e)}"}


class Sync:
    """主控同步器"""

    def __init__(self):
        self.master_instance = None  # 主控实例
        self.slave_instances = {}    # 被控实例
        self.sync_enabled = False    # 是否启用同步
        self.action_history = []     # 操作历史
        self.monitoring_thread = None
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
                window_index=0  # 主控实例在最左边
            )

            # 连接到主控实例
            print(f"正在连接主控实例: {master_name} ")
            if not self.master_instance.connect():
                return {"success": False, "error": f"连接主控实例失败: {master_name}"}
            # 初始化主控实例的 last_url
            try:
                self.master_instance.last_url = self.master_instance.tab.url
                print(f"主控实例当前URL: {self.master_instance.last_url}")
            except Exception as e:
                print(f"获取主控实例URL失败: {e}")
                self.master_instance.last_url = None

            # 连接其他实例作为被控实例
            connected_slaves = 0
            for index, process in enumerate(chrome_process[1:], start=1):  # 从第二个开始，索引从1开始
                slave_name = process["name"]
                slave_port = process.get('debugging_port')
                print(f"正在连接被控实例: {slave_name} (端口:{slave_port})")

                slave_controller = ChromeInstanceController(
                    name=slave_name,
                    port=slave_port,
                    window_index=index  # 被控实例依次排列在主控右侧
                )
                if slave_controller.connect():
                    self.slave_instances[slave_name] = slave_controller
                    connected_slaves += 1
                else:
                    print(f"连接被控实例失败: {slave_name}")

            # 自动启用同步模式
            self.sync_enabled = True

            # 设置主控实例的同步回调
            self.master_instance.sync_callback = self._sync_to_slaves
            self._start_monitoring()

            return {
                "success": True,
                "message": f"群控服务已启动！主控:{master_name} 将自动同步到 {connected_slaves} 个实例",
                "master": master_name,
                "total_instances": 1 + connected_slaves,
                "sync_enabled": True
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _start_monitoring(self):
        """启动监听线程"""
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            return
        self.monitoring_thread = threading.Thread(target=self._monitor_master, daemon=True)
        self.monitoring_thread.start()
        print("监听线程已启动，开始监听主控实例操作...")

    def _stop_monitoring(self):
        """停止监听线程"""
        self.sync_enabled = False
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            print("停止监听线程...")

    def _monitor_master(self):
        """监听主控实例的操作"""
        if not self.master_instance or not self.master_instance.tab:
            return

        loop_count = 0
        while self.sync_enabled and self.master_instance and self.master_instance.is_active:
            try:
                # self.master_instance.tab.
                loop_count += 1

                # 检查tab是否还有效，如果无效则重新获取
                try:
                    # 设置超时获取URL，避免因页面加载卡住
                    current_url = self._get_url_with_timeout()
                    if current_url is None:
                        print("URL获取超时，跳过本次检查")
                        time.sleep(1)
                        continue
                except Exception as tab_error:
                    print(f"Tab失效，尝试重新获取: {tab_error}")

                # 检查URL变化（导航操作）
                if current_url != self.master_instance.last_url:
                    print(f"检测到主控导航: {self.master_instance.last_url} -> {current_url}")
                    sync_result = self._sync_to_slaves("navigate", url=current_url)
                    print(f"同步结果: {sync_result}")
                    self.master_instance.last_url = current_url

                # 检查点击事件（通过页面变化检测）
                self._check_page_interactions()

                time.sleep(1)  # 每秒检查一次

            except Exception as e:
                print(f"监听过程中出错: {e}")
                print(f"错误详情: {str(e)}")
                time.sleep(2)  # 出错时延长等待

        # print("监听线程已停止")

    def _get_url_with_timeout(self, timeout=3):
        """带超时的URL获取，避免页面加载卡住"""
        import threading
        import time

        result = {'url': None, 'success': False}

        def get_url():
            try:
                result['url'] = self.master_instance.tab.url
                result['success'] = True
            except Exception as e:
                result['error'] = str(e)

        thread = threading.Thread(target=get_url)
        thread.daemon = True
        thread.start()
        thread.join(timeout)

        if thread.is_alive():
            # 超时了，说明页面可能在加载中
            return None

        if result['success']:
            return result['url']
        else:
            raise Exception(result.get('error', 'Unknown error'))

    def _check_page_interactions(self):
        """检查页面交互事件（简化实现）"""
        try:
            # 通过JavaScript检查页面是否有新的交互
            # 这是一个简化的实现，实际可以更复杂
            script = """
            // 检查页面是否有变化
            if (window.lastPageState === undefined) {
                window.lastPageState = {
                    scrollY: window.scrollY,
                    activeElement: document.activeElement ? document.activeElement.tagName : null
                };
                return null;
            }

            let currentState = {
                scrollY: window.scrollY,
                activeElement: document.activeElement ? document.activeElement.tagName : null
            };

            let changed = null;
            if (Math.abs(currentState.scrollY - window.lastPageState.scrollY) > 100) {
                changed = {type: 'scroll', scrollY: currentState.scrollY};
            }

            window.lastPageState = currentState;
            return changed;
            """

            result = self.master_instance.tab.run_js(script)
            if result and isinstance(result, dict):
                if result.get('type') == 'scroll':
                    print(f"检测到滚动操作: {result.get('scrollY')}")
                    self._sync_to_slaves("scroll", y=result.get('scrollY'))

        except Exception as e:
            # 静默处理交互检测错误，不影响主要监听
            pass

    def _sync_to_slaves(self, action: str, **kwargs):
        """同步操作到所有被控实例"""
        if not self.sync_enabled or not self.slave_instances:
            return

        print(f"同步操作到被控实例: {action}")

        # 记录操作历史
        operation = {
            "timestamp": time.time(),
            "action": action,
            "params": kwargs,
            "auto_sync": True
        }
        self.action_history.append(operation)

        # 同步到所有被控实例（并行执行，不等待完成）
        sync_results = {}
        for name, instance in self.slave_instances.items():
            if instance.is_active:
                try:
                    # 立即执行，不等待结果
                    result = instance.execute_action(action, **kwargs)
                    sync_results[name] = result

                    if result["success"]:
                        print(f"  成功 {name}: 同步开始")
                    else:
                        print(f"  警告 {name}: {result.get('error', '同步可能失败')}")

                except Exception as e:
                    print(f"  错误 {name}: 同步异常 - {e}")
                    # 继续处理其他实例，不中断

        return sync_results

    def shutdown(self):
        """关闭同步服务"""
        try:
            # 停止同步
            self.sync_enabled = False

            # 停止CDP监听
            if self.master_instance and self.master_instance.tab:
                try:
                    self.master_instance.tab.listen.stop('Page.frameNavigated')
                    print("已停止CDP事件监听")
                except Exception:
                    pass

            # 停止轮询监听线程
            self._stop_monitoring()

            # 断开所有连接
            if self.master_instance:
                self.master_instance.disconnect()
                self.master_instance = None

            for instance in self.slave_instances.values():
                instance.disconnect()

            self.slave_instances.clear()
            self.action_history.clear()

            return {"success": True, "message": "群控服务已关闭"}

        except Exception as e:
            return {"success": False, "error": f"关闭服务失败: {str(e)}"}

