import mouse
import win32process
import win32gui
import win32con
import win32api

lparam = win32api.MAKELONG(204, 17)
win32gui.PostMessage(3278970, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lparam)
win32gui.PostMessage(3278970, win32con.WM_LBUTTONUP, 0, lparam)