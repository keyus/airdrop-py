import winreg
import platform


class Chrome_App:
    def install(self, extension_id: str) -> None:
        print('install_chrome_extension', extension_id)
        try:
            # 检查系统架构并选择正确的注册表路径
            extensions_path = (
                r"Software\Wow6432Node\Google\Chrome\Extensions"
                if platform.machine().endswith('64')
                else r"Software\Google\Chrome\Extensions"
            )
            
            print(f"extension_id: {extension_id}")
            print(f"extensions_path: {extensions_path}")
            
            # 打开或创建 Extensions 键
            with winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE) as hklm:
                # 创建或打开 Extensions 键
                try:
                    extensions_key = winreg.CreateKeyEx(
                        hklm, 
                        extensions_path, 
                        0, 
                        winreg.KEY_ALL_ACCESS
                    )
                    print(f"extensions_key: {extensions_key}")
                    
                    # 为扩展创建子键
                    ext_key = winreg.CreateKeyEx(
                        extensions_key, 
                        extension_id, 
                        0, 
                        winreg.KEY_ALL_ACCESS
                    )
                    print(f"ext_key: {ext_key}")
                    
                    # 设置 update_url
                    winreg.SetValueEx(
                        ext_key,
                        "update_url",
                        0,
                        winreg.REG_SZ,
                        "https://clients2.google.com/service/update2/crx"
                    )
                    print("set update_url success")
                    
                    # 关闭键
                    winreg.CloseKey(ext_key)
                    winreg.CloseKey(extensions_key)
                    
                except WindowsError as e:
                    raise Exception(f"Failed to create/set registry key: {str(e)}")
                    
        except Exception as e:
            raise Exception(f"Error installing Chrome extension: {str(e)}")

    def uninstall(self, extension_id: str) -> None:
        try:
            # 检查系统架构
            extensions_path = (
                r"Software\Wow6432Node\Google\Chrome\Extensions"
                if platform.machine().endswith('64')
                else r"Software\Google\Chrome\Extensions"
            )
            
            # 打开注册表
            with winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE) as hklm:
                try:
                    # 首先检查扩展键是否存在
                    try:
                        extensions_key = winreg.OpenKey(
                            hklm,
                            extensions_path,
                            0,
                            winreg.KEY_READ
                        )
                        
                        # 尝试打开扩展子键检查是否存在
                        try:
                            winreg.OpenKey(extensions_key, extension_id)
                            # 扩展存在，关闭并重新打开以获取删除权限
                            winreg.CloseKey(extensions_key)
                            
                            # 重新打开带完全访问权限
                            extensions_key = winreg.OpenKey(
                                hklm,
                                extensions_path,
                                0,
                                winreg.KEY_ALL_ACCESS
                            )
                            # 删除扩展键
                            winreg.DeleteKey(extensions_key, extension_id)
                            print(f"Extension {extension_id} successfully uninstalled")
                        except WindowsError:
                            # 扩展不存在，不需要删除
                            print(f"Extension {extension_id} not found, no need to uninstall")
                        finally:
                            winreg.CloseKey(extensions_key)
                            
                    except WindowsError as e:
                        print(f"Extensions path not found: {str(e)}")
                        
                except WindowsError as e:
                    print(f"Failed to access registry: {str(e)}")
                    
        except Exception as e:
            print(f"Error uninstalling Chrome extension: {str(e)}")
