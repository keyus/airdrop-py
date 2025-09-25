
from .app import chrome_process
from .window.tools import Tools

class Sync:
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
  
