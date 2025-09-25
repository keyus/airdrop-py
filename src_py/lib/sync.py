
from .app import chrome_process
from .window_manager import WindowManager

class Sync:
    """主控同步器"""

    def __init__(self):
        self.master = None    # 主控实例
        self.children = {}    # 被控实例
        self.WindowManager = WindowManager()
         # 窗口管理器
        
    def start(self):
        if not chrome_process:
            return {"success": False, "error": "没有运行中的Chrome实例"}
        return self.WindowManager.windows_horizontal([item.get('pid') for item in chrome_process])

  
