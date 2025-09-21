import { createRoot } from "react-dom/client";
import { useMount } from "ahooks";
import { useState } from "react";
import { ConfigProvider, App as AntdApp, message } from 'antd'
import { rootContent } from '@/rootContext'
import { createHashRouter, RouterProvider, } from 'react-router'
import zhCN from 'antd/locale/zh_CN';
import App from "./App";
import Chrome from './pages/chrome'
import ChromeApp from './pages/chrome_app'
import Setting from './pages/setting'
import '@ant-design/v5-patch-for-react-19';


message.config({
    maxCount: 1,
});
function Main() {
    const [config, setConfig] = useState({});
    useMount(async () => {
        window.addEventListener('pywebviewready', async () => {
            const config = await window.pywebview.api.config.get_config();
            setConfig(config.data)
        })
    })
    const updateConfig = async (config_data: AppConfig) => {
        await window.pywebview.api.config.set_config(config_data)
        message.success('更新配置成功')
    }

    return (
        <rootContent.Provider value={{
            config,
            updateConfig,
        }}>
            <ConfigProvider
                locale={zhCN}
                theme={{
                    components: {
                        Table: {
                            headerBg: '#fff',
                            headerColor: '#bcbec5',
                            cellFontSize: 13,
                            footerBg: '#fff',
                            rowHoverBg: '#e9edfd',
                        }
                    }
                }}
            >
                <AntdApp>
                    <RouterProvider
                        router={createHashRouter([
                            {
                                path: '/',
                                element: <App />,
                                children: [
                                    {
                                        index: true,
                                        element: <Chrome />,
                                        handle: {
                                            title: '环境管理'
                                        }
                                    },
                                    {
                                        path: 'chrome_app',
                                        element: <ChromeApp />,
                                        handle: {
                                            title: '浏览器应用'
                                        }
                                    },
                                    {
                                        path: 'setting',
                                        element: <Setting />,
                                        handle: {
                                            title: 'app设置'
                                        }
                                    }
                                ]
                            },
                        ])}
                    />
                </AntdApp>
            </ConfigProvider>
        </rootContent.Provider>
    )
}
createRoot(document.getElementById("root")).render(<Main />);

