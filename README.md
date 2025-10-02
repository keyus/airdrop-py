


# Python + React


use rsbuild web server

#windows 64位
HKEY_LOCAL_MACHINE\SOFTWARE\WOW6432Node\Google\Chrome\Extensions

新建文件夹  扩展id
新建项  update_url

值  https://clients2.google.com/service/update2/crx

关于注册表如开发环境权限不足，可打开注册表 regedit手动为需要操作的键，添加用户权限


# 使用方法

### 创建虚拟环境
> py -m venv ./venv
> ./venv/Scripts/activate           #激活虚拟环境
> ./venv/Scripts/deactivate         #停止使用虚拟环境

#### 安装python依赖

> pip install -r requirements.txt

#### 安装前端
> npm install

#### 启动前端 server
> npm run dev

#### 构建前端文件 
> npm run build:frontend

#### 启动python 开发软件环境(先启动前端server后再执行)
> npm run start

#### 打包windows exe软件
> npm run build:windows


venv环境中安装
./venv/Scripts/pip.exe install DrissionPage