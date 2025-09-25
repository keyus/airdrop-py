import pywinauto
from pywinauto.win32functions import GetSystemMetrics

# 使用 pywinauto 内置函数
screen_width = GetSystemMetrics(0)   # SM_CXSCREEN
screen_height = GetSystemMetrics(1)  # SM_CYSCREEN

print(screen_width)
print(screen_height)