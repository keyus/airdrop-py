import { useMemo, useState, } from 'react'
import { Button, Modal, Input, Form, Tabs, Switch, } from 'antd'
import { useBoolean, useMount, } from 'ahooks';
import IpAuth from './IpAuth';

export default function ConfigNet({ onConfigWallet }:
    { onConfigWallet: () => void }
) {
    const [open, { toggle }] = useBoolean();

    return (
        <>
            <Button
                size='large'
                onClick={toggle}
            >
                环境配置
            </Button>
            <Modal
                title='环境配置'
                open={open}
                destroyOnClose
                mask={false}
                onCancel={toggle}
                footer={null}
            >
                <Tabs
                    items={[
                        {
                            key: 'url',
                            label: '启动网址',
                            children: <OpenUrlConfig onOk={toggle} />
                        },
                        {
                            key: 'proxy',
                            label: '代理配置',
                            children: <ProxyConfig onOk={toggle} />
                        },
                        {
                            key: 'wallet',
                            label: '钱包配置',
                            children: <WalletConfig onOk={() => {
                                onConfigWallet()
                                toggle()
                            }} />
                        },
                    ]}
                />


            </Modal>
        </>
    )
}


//钱包配置
function WalletConfig({ onOk }: { onOk: () => void }) {

    const [form] = Form.useForm();
    const walletConfigValue = Form.useWatch('walletConfig', form)
    const onSubmit = async ({ walletConfig }) => {
        if (walletConfig) {
            walletConfig = walletConfig.split('\n')
            walletConfig = walletConfig.map((item: string) => item.trim()).filter((item: string) => item)
        } else {
            walletConfig = []
        }
        await window.pywebview.api.app_config.set_wallet_config(walletConfig)
        window.message.success('钱包环境配置成功');
        onOk()
    }
    useMount(async () => {
        const config_wallet = await window.pywebview.api.app_config.get_wallet_config();
        const value = config_wallet.join('\n')
        form.setFieldsValue({
            walletConfig: value
        })
    })

    const walletlens = useMemo(() => {
        if (Array.isArray(walletConfigValue)) {
            return walletConfigValue.length
        } else {
            return walletConfigValue?.split('\n').length || 0
        }
    }, [walletConfigValue])

    return (
        <Form
            form={form}
            layout='vertical'
            onFinish={onSubmit}
        >
            <Form.Item
                name='walletConfig'
                rules={[{ required: true, message: '请输入钱包配置' }]}
                extra={`当前钱包数量：${walletlens}`}
            >
                <Input.TextArea rows={10} />
            </Form.Item>
            <Form.Item style={{ textAlign: 'right' }}>
                <Button
                    type='primary'
                    size='large'
                    onClick={() => {
                        form.submit()
                    }}
                >
                    保存钱包配置
                </Button>
            </Form.Item>
        </Form>
    )
}

//url配置
function OpenUrlConfig(props: { onOk: () => void }) {
    const { onOk } = props;
    const [form] = Form.useForm();
    const urlValue = Form.useWatch('url', form)
    const onSubmit = async ({ url, use }) => {
        if (url) {
            url = url.split('\n')
            url = url.map((item: string) => item.trim()).filter((item: string) => item)
        } else {
            url = []
        }
        await window.pywebview.api.app_config.set_url_config({
            url,
            use,
        })
        window.message.success('浏览器启动网址配置成功');
        onOk()
    }
    useMount(async () => {
        const urlConfig = await window.pywebview.api.app_config.get_url_config();
        const value = urlConfig.url.join('\n')
        const use = urlConfig.use
        form.setFieldsValue({
            url: value,
            use,
        })
    })

    const urlLens = useMemo(() => {
        if (Array.isArray(urlValue)) {
            return urlValue.filter(it => it).length
        } else {
            return urlValue?.split('\n').filter((it: any) => it).length || 0
        }
    }, [urlValue])
    return (
        <Form
            form={form}
            onFinish={onSubmit}
        >
            <Form.Item
                name='url'
                extra={`当前url数量：${urlLens}`}
            >
                <Input.TextArea rows={8} />
            </Form.Item>
            <Form.Item
                label='是否启用'
                name='use'
            >
                <Switch checkedChildren='启用' unCheckedChildren='禁用' />
            </Form.Item>
            <Form.Item
                style={{ textAlign: 'right' }}
            >
                <Button
                    type='primary'
                    htmlType='submit'
                    size='large'
                >
                    保存url配置
                </Button>
            </Form.Item>
        </Form>
    )
}



//代理配置
function ProxyConfig(props: { onOk: () => void }) {
    const { onOk } = props;
    const [form] = Form.useForm();
    const [updateLoading, setUpdateLoading] = useState(false);
    const proxyValue = Form.useWatch('proxy', form)
    const onSubmit = async ({ proxy, use }) => {
        if (proxy) {
            proxy = proxy.split('\n')
            proxy = proxy.map((item: string) => item.trim()).filter((item: string) => item)
        } else {
            proxy = []
        }
        await window.pywebview.api.app_config.set_proxy_config({
            proxy,
            use,
        })
        window.message.success('代理配置成功');
        onOk()
    }

    // 初始化表单数据
    const initData = async () => {
        const proxyConfig = await window.pywebview.api.app_config.get_proxy_config();
        const value = proxyConfig.proxy.join('\n');
        const use = proxyConfig.use;
        form.setFieldsValue({
            proxy: value,
            use,
        })
    }

    useMount(() => {
        initData()
    })

    const lens = useMemo(() => {
        if (Array.isArray(proxyValue)) {
            return proxyValue.filter(it => it).length
        } else {
            return proxyValue?.split('\n').filter((it: any) => it).length || 0
        }
    }, [proxyValue])

    const updateProxy = async () => {
        setUpdateLoading(true);
        await window.pywebview.api.webshare.update_proxy();
        window.message.success('代理更新成功');
        initData();
        setUpdateLoading(false);
    }

    return (
        <>
            <Form
                name='proxyConfig'
                form={form}
                onFinish={onSubmit}
            >
                <Form.Item
                    name='proxy'
                    extra={
                        <div>
                            当前有效的代理数量：{lens}
                            <Button
                                type='link'
                                loading={updateLoading}
                                onClick={updateProxy}>一键更新代理</Button>
                        </div>
                    }
                >
                    <Input.TextArea rows={8} />
                </Form.Item>
                <Form.Item
                    label='是否启用'
                    name='use'
                >
                    <Switch checkedChildren='启用' unCheckedChildren='禁用' />
                </Form.Item>

                <Form.Item
                    label='Ip授权'
                >
                    <IpAuth />
                </Form.Item>
                <Form.Item
                    style={{ textAlign: 'right' }}
                >
                    <Button
                        type='primary'
                        htmlType='submit'
                        size='large'
                    >
                        保存代理配置
                    </Button>
                </Form.Item>
            </Form>
        </>
    )
}
