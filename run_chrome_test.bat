@echo off
echo Chrome同步功能测试
echo ==================

echo 检查Python环境...
python --version
if %errorlevel% neq 0 (
    echo 错误: 未找到Python环境
    pause
    exit /b 1
)

echo.
echo 安装依赖...
pip install -r requirements_chrome.txt

echo.
echo 启动测试...
echo 注意: 测试需要管理员权限才能使用全局钩子
echo.

python test_chrome_sync.py

pause