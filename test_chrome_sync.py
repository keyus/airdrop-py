"""
Chrome同步功能测试脚本
测试简化版Chrome管理器的功能
"""
import time
import os
import sys
from src_py.lib.chrome_manager import SimpleChromeManager


def test_chrome_sync():
    """测试Chrome同步功能"""
    print("=== Chrome同步功能测试 ===\n")

    # 创建管理器
    manager = SimpleChromeManager()

    try:
        print("1. 创建Chrome实例...")

        # 确保配置文件目录存在
        profile_dirs = ["d:/test/1", "d:/test/2", "d:/test/3"]
        for profile_dir in profile_dirs:
            os.makedirs(profile_dir, exist_ok=True)

        # 创建3个Chrome实例
        print("   - 创建实例1...")
        instance1 = manager.create_instance(1, user_data_dir="d:/test/1")
        print(f"     实例1创建成功: 端口{instance1['port']}, 窗口{instance1['hwnd']}")

        print("   - 创建实例2...")
        instance2 = manager.create_instance(2, user_data_dir="d:/test/2")
        print(f"     实例2创建成功: 端口{instance2['port']}, 窗口{instance2['hwnd']}")

        # 等待Chrome完全启动
        print("\n2. 等待Chrome完全启动...")
        time.sleep(3)

        # 获取窗口信息
        print("\n3. 获取窗口信息...")
        windows = manager.get_all_windows()
        for window in windows:
            print(f"   - 实例{window['instance_id']}: {window['title']} (句柄:{window['hwnd']})")

        # 批量导航到测试页面
        print("\n4. 批量导航到测试页面...")
        test_url = "https://www.baidu.com"
        manager.batch_navigate([1, 2, 3], test_url)
        print(f"   已导航到: {test_url}")

        # 等待页面加载
        time.sleep(2)

        # 开始同步测试
        print("\n5. 启动同步功能...")
        print("   - 设置实例1为主控窗口")
        print("   - 设置实例2,3为被控窗口")
        manager.start_sync(master_instance_id=1, slave_instance_ids=[2, 3])
        print("   同步已启动!")

        # 交互提示
        print("\n" + "="*50)
        print("同步测试已启动!")
        print("请在实例1的Chrome窗口中进行操作:")
        print("- 鼠标移动、点击")
        print("- 键盘输入")
        print("- 滚轮滚动")
        print("操作应该会同步到实例2和实例3")
        print("="*50)
        print("\n按以下按键进行测试:")
        print("1 - 重新导航到百度")
        print("2 - 导航到Google")
        print("3 - 检查同步状态")
        print("s - 停止同步")
        print("r - 重启同步")
        print("q - 退出测试")

        # 交互循环
        while True:
            try:
                choice = input("\n请输入选择 (1/2/3/s/r/q): ").strip().lower()

                if choice == '1':
                    print("导航到百度...")
                    manager.batch_navigate([1, 2, 3], "https://www.baidu.com")

                elif choice == '2':
                    print("导航到Google...")
                    manager.batch_navigate([1, 2, 3], "https://www.google.com")

                elif choice == '3':
                    sync_status = "同步中" if manager.is_syncing() else "已停止"
                    print(f"同步状态: {sync_status}")
                    windows = manager.get_all_windows()
                    print("当前窗口:")
                    for window in windows:
                        print(f"   - 实例{window['instance_id']}: {window['title']}")

                elif choice == 's':
                    print("停止同步...")
                    manager.stop_sync()
                    print("同步已停止")

                elif choice == 'r':
                    if manager.is_syncing():
                        print("同步已在运行中")
                    else:
                        print("重启同步...")
                        manager.start_sync(master_instance_id=1, slave_instance_ids=[2, 3])
                        print("同步已重启")

                elif choice == 'q':
                    break

                else:
                    print("无效选择，请重新输入")

            except KeyboardInterrupt:
                break

    except Exception as e:
        print(f"测试过程中出错: {str(e)}")
        import traceback
        traceback.print_exc()

    finally:
        print("\n6. 清理资源...")
        manager.cleanup()
        print("测试完成!")


def test_basic_functionality():
    """基础功能测试"""
    print("=== 基础功能测试 ===\n")

    manager = SimpleChromeManager()

    try:
        # 确保配置文件目录存在
        os.makedirs("profiles/test", exist_ok=True)

        print("测试单个实例创建...")
        instance = manager.create_instance(99, user_data_dir="profiles/test")
        print(f"实例创建成功: 端口{instance['port']}")

        time.sleep(2)

        print("测试窗口检测...")
        windows = manager.get_all_windows()
        print(f"检测到{len(windows)}个窗口")

        print("测试实例关闭...")
        success = manager.close_instance(99)
        print(f"实例关闭: {'成功' if success else '失败'}")

    except Exception as e:
        print(f"基础测试失败: {str(e)}")
    finally:
        manager.cleanup()


if __name__ == "__main__":
    print("Chrome同步功能测试工具")
    print("请确保已安装必要依赖: win32gui, keyboard, mouse, requests")
    print()

    if len(sys.argv) > 1 and sys.argv[1] == "basic":
        test_basic_functionality()
    else:
        test_chrome_sync()