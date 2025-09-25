#!/usr/bin/env python3
"""
Chrome窗口排列示例 - 使用纯ctypes实现
"""

from src_py.lib.sync import Sync

def main():
    # 创建同步器实例
    sync = Sync()

    print("=== Chrome窗口排列示例 ===")
    print("请确保已经启动了多个Chrome实例")

    # 方式1: 启动完整的同步功能（包含窗口排列）
    print("\n1. 启动完整同步功能（水平排列 + 同步）:")
    result = sync.start()
    print(f"结果: {result}")

    # 等待用户输入
    input("\n按Enter继续测试其他排列方式...")

    # 方式2: 只进行水平排列
    print("\n2. 仅水平排列窗口:")
    result = sync.arrange_windows_horizontal()
    print(f"结果: {result}")

    input("\n按Enter继续...")

    # 方式3: 网格排列 (2x2)
    print("\n3. 网格排列 (2行2列):")
    result = sync.arrange_windows_grid(rows=2, cols=2)
    print(f"结果: {result}")

    input("\n按Enter继续...")

    # 方式4: 自定义水平排列（指定窗口大小）
    print("\n4. 自定义水平排列（窗口宽度400px, 高度600px）:")
    result = sync.arrange_windows_horizontal(window_width=400, window_height=600)
    print(f"结果: {result}")

    print("\n=== 演示完成 ===")

if __name__ == "__main__":
    main()