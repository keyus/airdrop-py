
from DrissionPage import Chromium, ChromiumOptions

class Sync:
    def start(self):
        try:
            # 创建Chrome实例
            browser = Chromium('127.0.0.1:9223')
            tab = browser.latest_tab
            tab.get('http://baidu.com')

            return {"success": True, "message": "浏览器启动成功"}
        except Exception as e:
            return {"success": False, "error": str(e)}

