import { useState } from "react";
import { useBoolean, useMount } from "ahooks";
import { createRoot } from "react-dom/client";
import { ConfigContext, initConfigValue } from '@/rootContext'
import { ConfigProvider, App as AntdApp, message, Skeleton } from 'antd'
import { createHashRouter, RouterProvider, } from 'react-router'
import App from "./App";
import zhCN from 'antd/locale/zh_CN';
import Chrome from './pages/chrome'
import ChromeApp from './pages/chrome_app'
import Setting from './pages/setting'
import '@ant-design/v5-patch-for-react-19';

message.config({
    maxCount: 1,
});

function Main() {
    const [config, setConfig] = useState<AppConfig>(initConfigValue);
    const [loading, { toggle }] = useBoolean(true)
    useMount(async () => {
        window.addEventListener('pywebviewready', async () => {
            window.py = window.pywebview.api;
            toggle()
            init();
        })
    })
    const updateConfig = async (newConfig: AppConfig) => {
        await window.py.config.set_config(newConfig);
        message.success('配置保存成功');
        init()
    }
    const init = async () => {
        const config = await window.py.config.get_config();
        setConfig(config.data)
    }
    return (
        <AntdApp className="root-app">
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
                <ConfigContext value={{
                    config,
                    refreshConfig: init,
                    updateConfig,
                    loading,
                }}>
                    <RouterProvider
                        router={createHashRouter([
                            {
                                path: '/',
                                element: <App />,
                                children: [
                                    {
                                        index: true,
                                        element: <Skeleton loading={loading}><Chrome /></Skeleton>,
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
                </ConfigContext>
            </ConfigProvider>
        </AntdApp>
    )
}

createRoot(document.getElementById("root") as HTMLElement).render(<Main />);

