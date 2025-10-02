import win32api
import win32con

# hwnd=0 表示没有父窗口
win32api.MessageBox(0, "chrome浏览器同步已开启", "提示", win32con.MB_OK | win32con.MB_ICONINFORMATION)