import os

# 用户AppData目录
app_data = os.environ.get("appdata")
user_data_path = os.path.join(app_data, "com.airdrop.py")
# config json 位置
config_path = os.path.join(user_data_path, "config.json")
webshare_path = os.path.join(user_data_path, "webshare.txt")

chrome_install_path = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
user_data_dir = "--user-data-dir=d:\\chrome100 app\\"
telegram_install_path = "D:\\telegram100-app\\"