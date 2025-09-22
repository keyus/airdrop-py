
from DrissionPage import Chromium
from typing import Dict, List, Any
import threading
import time
import json
from .app import chrome_process, config_handle


class ChromeInstanceController:
    """单个Chrome实例控制器"""

    def __init__(self, name: str, port: int, ):
        self.name = name
        self.port = port
        self.browser = None
        self.tab = None
        self.is_active = False
        self.last_url = None
        self.sync_callback = None  # 同步回调函数

    def connect(self) -> bool:
        """连接到现有Chrome实例"""
        try:
            # 连接到已运行的Chrome实例
            self.browser = Chromium(f'127.0.0.1:{self.port}')
            self.tab = self.browser.latest_tab
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
                # 只是断开连接，不关闭浏览器
                self.browser = None
                self.tab = None
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
        """启动群控同步服务 - 一键启动完整群控功能"""
        try:
            print("开始启动群控服务...")
            print(f"当前Chrome进程列表: {chrome_process}")

            # 获取当前运行的Chrome进程
            if not chrome_process:
                return {"success": False, "error": "没有运行中的Chrome实例，请先启动Chrome"}

            print(f"找到 {len(chrome_process)} 个Chrome进程")

            # 以第一个Chrome进程作为主控实例
            master_process = chrome_process[0]
            master_name = master_process["name"]
            master_port = master_process.get('debugging_port')
            print(f"选择主控实例: {master_name} (端口: {master_port})")

            # 创建主控实例控制器
            self.master_instance = ChromeInstanceController(
                name=master_name,
                port=master_port,
            )

            # 连接到主控实例
            print(f"正在连接主控实例: {master_name} (端口:{master_port})")
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
            for process in chrome_process[1:]:  # 从第二个开始
                slave_name = process["name"]
                slave_port = process.get('debugging_port')
                print(f"正在连接被控实例: {slave_name} (端口:{slave_port})")

                slave_controller = ChromeInstanceController(
                    name=slave_name,
                    port=slave_port,
                )
                if slave_controller.connect():
                    self.slave_instances[slave_name] = slave_controller
                    connected_slaves += 1
                else:
                    print(f"连接被控实例失败: {slave_name}")

            # 自动启用同步模式
            self.sync_enabled = True
            print(f"已启用同步模式，连接的被控实例数: {connected_slaves}")

            # 设置主控实例的同步回调
            self.master_instance.sync_callback = self._sync_to_slaves

            # 启动监听线程
            self._start_monitoring()
            print(f"监听线程启动状态: {self.monitoring_thread.is_alive() if self.monitoring_thread else 'None'}")

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

        print(f"开始监听主控实例: {self.master_instance.name}")

        loop_count = 0
        while self.sync_enabled and self.master_instance and self.master_instance.is_active:
            try:
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
                    try:
                        self.master_instance.tab = self.master_instance.browser.latest_tab
                        current_url = self._get_url_with_timeout()
                        if current_url is None:
                            print("重新获取Tab后URL仍然超时")
                            time.sleep(2)
                            continue
                        print("Tab重新获取成功")
                    except Exception as retry_error:
                        print(f"Tab重新获取失败: {retry_error}")
                        time.sleep(2)
                        continue

                # 每10秒输出一次监听状态
                if loop_count % 10 == 1:
                    print(f"监听中... (第{loop_count}次) 当前URL: {current_url}")

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

        print("监听线程已停止")

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

    def master_execute(self, action: str, **kwargs) -> Dict[str, Any]:
        """在主控实例执行操作并同步到被控实例"""
        if not self.master_instance or not self.master_instance.is_active:
            return {"success": False, "error": "主控实例未连接"}

        try:
            # 在主控实例执行操作
            master_result = self.master_instance.execute_action(action, **kwargs)

            if master_result["success"]:
                # 自动同步到被控实例
                sync_results = self._sync_to_slaves(action, **kwargs)

                return {
                    "success": True,
                    "master_result": master_result,
                    "sync_results": sync_results,
                    "message": f"主控操作成功，已同步到 {len(self.slave_instances)} 个实例"
                }
            else:
                return {
                    "success": False,
                    "error": f"主控操作失败: {master_result.get('error', '未知错误')}"
                }

        except Exception as e:
            return {"success": False, "error": f"执行操作失败: {str(e)}"}

    def shutdown(self):
        """关闭同步服务"""
        try:
            # 停止监听
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

    def get_status(self) -> Dict[str, Any]:
        """获取同步服务状态"""
        return {
            "sync_enabled": self.sync_enabled,
            "master_instance": self.master_instance.name if self.master_instance else None,
            "slave_count": len(self.slave_instances),
            "slave_instances": list(self.slave_instances.keys()),
            "total_operations": len(self.action_history)
        }

