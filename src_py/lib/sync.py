
from .app import chrome_process
from .window.tools import Tools
from pywinauto.win32_hooks import Hook

class Sync:
    def __init__(self):
        self.hook = None
    def arrange_windows_horizontal(self):
        """使用pywinauto水平排列Chrome窗口"""
        try:
            for i, process_item in enumerate(chrome_process):
                app = process_item.get('app')
                if not app.is_process_running():
                    continue
                tools = Tools(app, i)
                tools.set_win_pos()
            return {"success": True, "message": f"成功排列 {len(chrome_process)} 个窗口"}
        except Exception as e:
            return {"success": False, "message": f"排列窗口时出错: {str(e)}"}
    def start(self):
        if len(chrome_process) < 2:
            return {"success": False, "message": "没有可同步实例"}
        self.arrange_windows_horizontal()
        self.sync_hooks()
        
    def stop(self):
        if self.hook:
            self.hook.stop()
            self.hook = None
            print('同步已停止stop hooks')
  
    # 同步鼠标，键盘
    def sync_hooks(self):
        self.hook = Hook()
        self.hook.handler = self.event_handler
        self.hook.hook(keyboard=True, mouse=True)
        if self.hook:
            self.hook.listen()
        
    # 同步事件回调
    def event_handler(self,event):
        """事件处理函数"""
        if hasattr(event, 'event_type'):
            event_type = event.event_type
        else:
            event_type = type(event).__name__
        if hasattr(event, 'key'):
            key = event.key
            print(f"键盘事件: {event_type} - 按键: {key}")
        elif hasattr(event, 'button'):
            button = event.button
            print(f"鼠标事件: {event_type} - 按钮: {button}")
        else:
            print(f"事件: {event_type}")
            # 打印事件对象的所有属性
            attrs = [attr for attr in dir(event) if not attr.startswith('_')]
            for attr in attrs:
                try:
                    value = getattr(event, attr)
                    if not callable(value):
                        print(f"  {attr}: {value}")
                except:
                    pass

