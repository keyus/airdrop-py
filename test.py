from pywinauto.win32_hooks import Hook
import time

# 创建全局变量存储事件
events = []
def event_handler(event):
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

    events.append(event)

try:
    hook = Hook()
    hook.handler = event_handler
    hook.hook(keyboard=True, mouse=True)
    hook.listen()
except KeyboardInterrupt:
    hook.stop()
    print("钩子已停止")
except Exception as e:
    print(f"发生错误: {e}")
    hook.stop()